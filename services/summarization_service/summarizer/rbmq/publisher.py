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
            exchange_type: str = "",
            confirm_delivery: bool = True,
            exclusive: bool = False,
            durable: bool = True,
            auto_delete: bool = False,
            connection_timeout: Optional[float] = None,
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
                connection_timeout (float): The timeout for the connection to the broker.
                dead_letter_handling (bool): Whether to enable dead letter handling or not.
                message_ttl (int): The time to live for messages in milliseconds.
                dead_letter_exchange (str): The name of the exchange to publish dead letters to.
                dead_letter_routing_key (str): The routing key to use when publishing dead letters.
            """
            self.queue = queue
            self.routing_key = routing_key
            self.exchange_name = exchange_name
            self.exchange_type = exchange_type
            self.confirm_delivery = confirm_delivery
            self.exclusive = exclusive
            self.durable = durable
            self.auto_delete = auto_delete
            self.connection_timeout = connection_timeout
            self.dead_letter_handling = dead_letter_handling
            self.message_ttl = message_ttl
            self.dead_letter_exchange = dead_letter_exchange
            self.dead_letter_routing_key = dead_letter_routing_key

    def __init__(
        self,
        connect_params: pika.ConnectionParameters,
        type_config: PublisherTypeConfig,
    ):
        """
        Initializes the publisher.
        Args:
            connect_params (pika.ConnectionParameters): The connection parameters for the broker.
            type_config (PublisherTypeConfig): The configuration object for the publisher type.
        """
        self.connect_params = connect_params
        self.type_config = type_config
        self.connection = None
        self.channel = None

        self.is_connected = False
        self._max_retries_connection = 10

        self.logging = logging.getLogger(__name__)
        self.logging.setLevel(logging.INFO)

    def _connect(self):
        """
        Connects to the broker.
        """
        if self.is_connected:
            raise Exception("Publisher is already connected.")
        # Connect to the broker.

        self.logging.info(
            f"[x] - Connecting to RabbitMQ server: amqp://{self.connect_params.host}:{self.connect_params.port}"
        )

        self.connection = pika.BlockingConnection(
            self.connect_params, self.type_config.connection_timeout
        )

        self.logging.info(
            "[x] - Connected to RabbitMQ server: amqp://%s:%s",
            self.connect_params.host,
            self.connect_params.port,
        )
        ## Add a info log with time stamp in format [timestamp] [x] - message

        self.logging.info("[x]- Creating channel")
        self.channel = self.connection.channel()
        self.logging.info("[x]- Channel created")

        # Enable publisher confirms if needed.
        if self.type_config.confirm_delivery:
            self.channel.confirm_delivery()

        self.is_connected = True

    def connect(self):
        """
        Connects to the broker.
        """
        num_of_retries = self._max_retries_connection
        while True:
            try:
                self._connect()
                self._setup_channel()
                break

            except pika.exceptions.AMQPConnectionError as e:

                self.logging.error("Error connecting to RabbitMQ server: %s\n", e)
                self.logging.error("Retrying in 3 seconds...\n")
                self.logging.error("Remaining retries: %s\n", num_of_retries)

                num_of_retries -= 1
                if num_of_retries == 0:
                    raise e
                time.sleep(3)

        return True

    def _setup_channel(self):
        # Declare the exchange.
        if self.channel.is_open:

            if self.type_config.exchange_name and self.type_config.exchange_type:
                self.channel.exchange_declare(
                    exchange=self.type_config.exchange_name,
                    exchange_type=self.type_config.exchange_type,
                    durable=self.type_config.durable,
                    auto_delete=self.type_config.auto_delete,
                )

            if self.type_config.queue:
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

            self.logging.info(f" [{datetime.datetime.now()}] : Message was delivered")

            return True

        except Exception as e:
            self.logging.warning(
                f" [{datetime.datetime.now()}] : Message was not delivered"
            )
            if isinstance(e, pika.exceptions.UnroutableError):
                self.logging.error(
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
