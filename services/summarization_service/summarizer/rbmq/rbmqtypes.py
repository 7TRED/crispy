import json
from typing import Any, Dict, Optional

import pika

"""This module contains the base class for all messages sent over RabbitMQ. """


class RMQMessage(object):

    """Base class for all messages sent over RabbitMQ."""

    def __init__(
        self,
        payload: Dict[str, Any],
        mandatory: bool = True,
        properties=Optional[pika.BasicProperties],
    ) -> None:
        """Initializes the message object.
        Args:
            payload (dict): The payload of the message.
            mandatory (bool): Whether the message is mandatory or not.
            properties (pika.BasicProperties): The properties of the message.
        """
        self.payload: Dict[str, Any] = payload
        self.properties: Optional[pika.BasicProperties] = properties
        self.mandatory: bool = mandatory
        self.retries = 0

    @classmethod
    def from_dict(cls, message_dict: Dict[str, Any]) -> "RMQMessage":
        """Creates a message object from a dictionary.
        Args:
            message_dict (dict): A dictionary representation of the message object.
        Returns:
            RMQMessage: A message object.
        """
        return cls(
            payload=message_dict["payload"],
            mandatory=message_dict["mandatory"],
            properties=message_dict["properties"],
        )

    @classmethod
    def from_json(
        cls, message_json: str, properties: Optional[pika.BasicProperties] = None
    ) -> "RMQMessage":
        """Creates a message object from a JSON string.
        Args:
            message_json (str): A JSON string representation of the message object.
            properties (pika.BasicProperties): The properties of the message.
        Returns:
            RMQMessage: A message object.
        """
        message_dict = json.loads(message_json)
        message_dict["properties"] = properties
        return cls.from_dict(message_dict)

    def __repr__(self) -> str:
        """Returns a string representation of the message object.
        Returns:
            str: A string representation of the message object.
        """
        return f"RMQMessage(payload={self.payload}, mandatory={self.mandatory})"

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the message object.
        Returns:
            dict: A dictionary representation of the message object.
        """
        return {
            "payload": self.payload,
            "mandatory": self.mandatory,
        }

    def to_json(self) -> str:
        """Returns a JSON representation of the message object.
        Returns:
            str: A JSON representation of the message object.
        """
        return json.dumps(self.to_dict())
