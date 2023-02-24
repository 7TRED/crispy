import os
import sys

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
    rmq_queue = os.environ.get("RMQ_QUEUE", "guest")
    rmq_exchange = os.environ.get("RMQ_EXCHANGE", "guest")
    rmq_routing_key = os.environ.get("RMQ_ROUTING_KEY", "guest")

    connect_config = Listener.ListenerConnectConfig(rmq_host, rmq_port)
    type_config = Listener.ListenerTypeConfig(
        queue=rmq_queue,
        exchange_name=rmq_exchange,
        exchange_type="topic",
        routing_key=rmq_routing_key,
    )
    listener = Listener(connect_config, type_config)
    listener.on_message(message_callback=callback)


if __name__ == "__main__":
    main()
