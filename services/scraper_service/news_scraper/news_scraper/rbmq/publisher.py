import datetime
import logging
import time
from typing import Optional

import pika

from .rbmqtypes import RMQMessage


class Publisher:
    """
    A class for publishing messages to a RabbitMQ broker.
    """

    class PublisherTypeConfig:
        def __init__(
            self,
            queue: Optional[str] = None,
            routing_key: Optional[str] = None,
            exchange_name: str = "",
            exchange_type: str = "direct",
            confirm_delivery: bool = True,
            exclusive: bool = False,
            durable: bool = True,
            auto_delete: bool = False,
            dead_letter_handling: bool = False,
            message_ttl: Optional[int] = None,
            dead_letter_exchange: Optional[str] = None,
            dead_letter_routing_key: Optional[str] = None,
        ):
            """
            Initializes the configuration object for a publisher.

            Args:
                queue (str): The name of the queue to publish to.
                exchange_name (str): The name of the exchange to publish to.
                exchange_type (str): The type of the exchange to publish to (e.g. 'direct', 'fanout', 'topic', etc.).
                confirm_delivery (bool): Whether to use publisher confirms or not.
                exclusive (bool): Whether the queue should be exclusive to the publisher or not.
                durable (bool): Whether the queue/exchange should persist after the broker restarts or not.
                auto_delete (bool): Whether the queue/exchange should be deleted after the last consumer disconnects or not.
            """
            self.queue = queue
            self.routing_key = routing_key
            self.exchange_name = exchange_name
            self.exchange_type = exchange_type
            self.confirm_delivery = confirm_delivery
            self.exclusive = exclusive
            self.durable = durable
            self.auto_delete = auto_delete
            self.dead_letter_handling = dead_letter_handling
            self.message_ttl = message_ttl
            self.dead_letter_exchange = dead_letter_exchange
            self.dead_letter_routing_key = dead_letter_routing_key

    class PublisherConnectConfig:
        def __init__(
            self,
            host: str = "localhost",
            port: str = 5672,
            virtual_host: str = "/",
            username: str = "guest",
            password: str = "guest",
        ):
            """
            Initializes the configuration object for a publisher connection.

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
        self, connect_config: PublisherConnectConfig, type_config: PublisherTypeConfig
    ):
        """
        Initializes the publisher.

        Args:
            config (PublisherConnectConfig): The configuration object for the publisher connection.
        """
        self.connect_config = connect_config
        self.type_config = type_config
        self.connection = None
        self.channel = None

        self.is_connected = False
        self._max_retries_connection = 10

    def _connect(self):
        """
        Connects to the broker.
        """
        if self.is_connected:
            raise Exception("Publisher is already connected.")
        # Connect to the broker.
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connect_config.host,
                port=self.connect_config.port,
                credentials=self.connect_config.credentials,
                virtual_host=self.connect_config.virtual_host,
            )
        )

        self.channel = self.connection.channel()

        # Enable publisher confirms if needed.
        if self.type_config.confirm_delivery:
            self.channel.confirm_delivery()

        self.is_connected = True

    def connect(self):
        """
        Connects to the broker.
        Args:
            config (PublisherTypeConfig): The configuration object for the publisher type.
        """
        num_of_retries = self._max_retries_connection
        while True:
            try:
                self._connect()
                self._setup_channel()
                break
            except Exception as e:
                logging.error("Error connecting to RabbitMQ server: %s\n", e)
                logging.error("Retrying in 3 seconds...\n")
                logging.error("Remaining retries: %s\n", num_of_retries)
                num_of_retries -= 1
                if num_of_retries == 0:
                    raise e
                time.sleep(3)

        return True

    def _setup_channel(self):
        # Declare the exchange.
        self.channel.exchange_declare(
            exchange=self.type_config.exchange_name,
            exchange_type=self.type_config.exchange_type,
            durable=self.type_config.durable,
            auto_delete=self.type_config.auto_delete,
        )

        if self.type_config.exchange_type == "direct" or self.type_config.queue:
            # If the exchange type is direct, we need to declare a queue and bind it to the exchange.
            args = {}
            if self.type_config.dead_letter_handling:
                if self.type_config.dead_letter_exchange is None:
                    self.type_config.dead_letter_exchange = (
                        self.type_config.exchange_name
                    )

                elif (
                    self.type_config.dead_letter_exchange
                    != self.type_config.exchange_name
                ):
                    self.channel.exchange_declare(
                        exchange=self.type_config.dead_letter_exchange,
                        exchange_type="direct",
                        durable=self.type_config.durable,
                        auto_delete=self.type_config.auto_delete,
                    )

                if self.type_config.dead_letter_routing_key is None:
                    self.type_config.dead_letter_routing_key = (
                        self.type_config.routing_key
                    )

                args = {
                    "x-dead-letter-exchange": self.type_config.dead_letter_exchange,
                    "x-dead-letter-routing-key": self.type_config.dead_letter_routing_key,
                }
                if self.type_config.message_ttl:
                    args["x-message-ttl"] = self.type_config.message_ttl

            self.channel.queue_declare(
                queue=self.type_config.queue,
                exclusive=self.type_config.exclusive,
                durable=self.type_config.durable,
                auto_delete=self.type_config.auto_delete,
                arguments=args,
            )
            self.channel.queue_bind(
                exchange=self.type_config.exchange_name,
                queue=self.type_config.queue,
                routing_key=self.type_config.routing_key,
            )

    def publish(self, message: RMQMessage):
        """
        Publishes a message to the broker.
        Args:
            message (RMQMessage): The message to publish.
            properties (pika.BasicProperties): The properties of the message.

        Returns:
            bool: Whether the message was delivered or not.
        """
        try:
            self.channel.basic_publish(
                exchange=self.type_config.exchange_name,
                routing_key=self.type_config.routing_key,
                body=message.to_json(),
                properties=message.properties,
                mandatory=message.mandatory,
            )

            logging.info(f" [{datetime.datetime.now()}] : Message was delivered")

            return True

        except pika.exceptions.UnroutableError or pika.exceptions.NackError as e:
            logging.warning(f" [{datetime.datetime.now()}] : Message was not delivered")
            if isinstance(e, pika.exceptions.UnroutableError):
                logging.error(
                    f" [{datetime.datetime.now()}] : Message was not delivered. UnroutableError"
                )
            return False

    def close(self):
        """
        Closes the connection to the broker.

        """
        self.channel.close()
        self.connection.close()
        self.is_connected = False
