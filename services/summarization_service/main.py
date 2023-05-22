import os
import sys

import pika

from rbmq.listener import Listener
from rbmq.rbmqtypes import RMQMessage


def main():
    print("Starting listener")

    @Listener.RMQMessageCallback
    def callback(ch, method, message: RMQMessage, handle_nack: callable = None):
        print(" [x] Received %r" % message.payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    rmq_host = os.environ.get("RMQ_HOST", "localhost")
    rmq_port = os.environ.get("RMQ_PORT", 5672)
    rmq_user = os.environ.get("RMQ_USER")
    rmq_pass = os.environ.get("RMQ_PASS")
    rmq_queue = os.environ.get("RMQ_QUEUE")
    rmq_exchange = os.environ.get("RMQ_EXCHANGE")
    rmq_routing_key = os.environ.get("RMQ_ROUTING_KEY")

    connect_params = pika.ConnectionParameters(
        host=rmq_host,
        port=rmq_port,
        credentials=pika.PlainCredentials(rmq_user, rmq_pass),
    )
    type_config = Listener.ListenerTypeConfig(
        queue=rmq_queue,
        exchange_name=rmq_exchange,
        exchange_type="topic",
        routing_key=rmq_routing_key,
    )
    listener = Listener(connect_params, type_config)
    listener.on_message(message_callback=callback)


if __name__ == "__main__":
    main()
