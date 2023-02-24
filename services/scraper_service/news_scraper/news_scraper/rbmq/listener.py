import logging
import os
import sys
import time
from types import FunctionType
from typing import Optional

import pika

from .rbmqtypes import RMQMessage


class Listener:
    """
    A class for listening to messages from a RabbitMQ broker.
    """

    # Constants
    MAX_RETRIES_NACK = 5
    RETRY_DELAY = 2

    class ListenerTypeConfig:
        def __init__(
            self,
            queue: Optional[str] = None,
            routing_key: Optional[str] = None,
            exchange_name: str = "",
            exchange_type: str = "direct",
            durable: bool = True,
            exclusive: bool = False,
            auto_delete: bool = False,
            prefetch_count: int = 1,
        ):
            """
            Initializes the configuration object for a listener.

            Args:
                queue (str): The name of the queue to consume from.
                routing_key (str): The routing key to use when binding the queue to the exchange.
                exchange_name (str): The name of the exchange to consume from.
                exchange_type (str): The type of the exchange to consume from (e.g. 'direct', 'fanout', 'topic', etc.).
                durable (bool): Whether the queue/exchange should persist after the broker restarts or not.
                exclusive (bool): Whether the queue should be exclusive to the consumer or not.
                auto_delete (bool): Whether the queue/exchange should be deleted after the last consumer disconnects or not.
                prefetch_count (int): The maximum number of unacknowledged messages the consumer can have at a time.
            """
            self.queue = queue
            self.routing_key = routing_key
            self.exchange_name = exchange_name
            self.exchange_type = exchange_type
            self.durable = durable
            self.exclusive = exclusive
            self.auto_delete = auto_delete
            self.prefetch_count = prefetch_count

    class ListenerConnectConfig:
        def __init__(
            self,
            host: str = "localhost",
            port: int = 5672,
            virtual_host: str = "/",
            username: str = "guest",
            password: str = "guest",
        ):
            """
            Initializes the configuration object for a listener connection.

            Args:
                host (str): The host of the broker to connect to.
                port (int): The port of the broker to connect to.
                username (str): The username to use for authentication.
                password (str): The password to use for authentication.
            """
            self.host = host
            self.port = port
            self.virtual_host = virtual_host
            self.credentials = pika.PlainCredentials(username, password)

    def __init__(
        self,
        connect_config: ListenerConnectConfig,
        type_config: ListenerTypeConfig,
    ):
        """
        Initializes the listener.

        Args:
            connect_config (ListenerConnectConfig): The configuration object for the listener connection.
            type_config (ListenerTypeConfig): The configuration object for the listener type.
            message_callback (callable): A callback function to be called when a message is received.
        """
        self.connect_config = connect_config
        self.type_config = type_config
        self.message_callback = None
        self._connection = None
        self._channel = None
        self._is_connected = False
        self._is_consuming = False

        self._max_retries_nack = 5
        self._retries_nack = 0
        self._max_retries_connection = 10

    def _connect(self):
        """
        Connects to the RabbitMQ server and creates a channel.
        """
        logging.info(
            "Connecting to RabbitMQ server at %s:%s",
            self.connect_config.host,
            self.connect_config.port,
        )

        if self._is_connected:
            raise Exception("Already connected to RabbitMQ server.")

        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connect_config.host,
                port=self.connect_config.port,
                virtual_host=self.connect_config.virtual_host,
                credentials=self.connect_config.credentials,
            )
        )
        self._channel = self._connection.channel()
        self._is_connected = True

    def connect(self):
        """
        Connects to the RabbitMQ server and creates a channel.
        """
        num_of_retry = self._max_retries_connection
        while True:
            try:
                logging.info(
                    "Retrying connection to RabbitMQ server at %s:%s",
                    self.connect_config.host,
                    self.connect_config.port,
                )
                self._connect()
                break
            except Exception as e:
                logging.error("Error connecting to RabbitMQ server: %s\n", e)
                logging.error("Retrying in 3 seconds...\n")
                logging.error("Remaining retries: %s\n", num_of_retry)
                num_of_retry -= 1
                if num_of_retry == 0:
                    raise e
                time.sleep(3)

        return True

    def _setup_channel(self):
        """
        Sets up the queue and exchange for the listener.

        """
        logging.info("Setting up queue and exchange for listener.")
        self._channel.exchange_declare(
            exchange=self.type_config.exchange_name,
            exchange_type=self.type_config.exchange_type,
            durable=self.type_config.durable,
            auto_delete=self.type_config.auto_delete,
        )

        self._channel.queue_declare(
            queue=self.type_config.queue,
            durable=self.type_config.durable,
            exclusive=self.type_config.exclusive,
            auto_delete=self.type_config.auto_delete,
        )

        self._channel.queue_bind(
            exchange=self.type_config.exchange_name,
            queue=self.type_config.queue,
            routing_key=self.type_config.routing_key,
        )

        self._channel.basic_qos(prefetch_count=self.type_config.prefetch_count)
        self._channel.basic_consume(
            queue=self.type_config.queue, on_message_callback=self.message_callback
        )

    def on_message(self, message_callback: callable = None):
        if not self._is_connected:
            self.connect()

        if self._is_consuming:
            raise Exception("Already consuming messages.")

        if not isinstance(message_callback, FunctionType):
            raise Exception("Invalid message callback.")

        self.message_callback = message_callback
        self._setup_channel()

        try:
            logging.info("Starting to consume messages.\n")
            self._channel.start_consuming()
            self._is_consuming = True
        except KeyboardInterrupt:
            logging.info("Stopping to consume messages.\n")
            self.close()

    def close(self):
        """
        Closes the connection to the RabbitMQ server.
        """
        logging.info("Closing connection to RabbitMQ server.")
        if self._is_consuming:
            self._channel.stop_consuming()
            self._is_consuming = False

        self._channel.close()
        self._connection.close()
        self._is_connected = False

        return True

    @classmethod
    def RMQMessageCallback(cls, message_callback: callable):

        retries_nack = 0

        def handle_nack(
            ch, delivery_tag, message: RMQMessage, requeue=True, multiple=False
        ):
            """
            Handles nacking a message.

            """
            nonlocal retries_nack
            retries_nack += 1
            if retries_nack >= cls.MAX_RETRIES_NACK:
                logging.error("Max retries reached for message: %s", message.to_json())
                logging.error("Dropping message: %s", message.to_json())
                ch.basic_nack(
                    delivery_tag=delivery_tag, requeue=False, multiple=multiple
                )

                retries_nack = 0
                return

            time.sleep(cls.RETRY_DELAY)
            ch.basic_nack(delivery_tag=delivery_tag, requeue=requeue, multiple=multiple)
            logging.error("Nacking message: %s", message.to_json())

        def wrapper(ch, method, properties, body):
            message = RMQMessage.from_json(body, properties=properties)
            message_callback(ch, method, message, handle_nack)

        return wrapper


def main():
    @Listener.RMQMessageCallback
    def callback(ch, method, message: RMQMessage, handle_nack: callable = None):
        print(" [x] Received %r" % message.message_type)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connect_config = Listener.ListenerConnectConfig("localhost")
    type_config = Listener.ListenerTypeConfig(
        queue="test_1",
        exchange_name="test_exchange",
        exchange_type="direct",
        routing_key="test_routing_key",
    )
    listener = Listener(connect_config, type_config)
    listener.on_message(message_callback=callback)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
