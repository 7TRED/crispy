import os
import sys

import pika

from rbmq.listener import Listener
from rbmq.rbmqtypes import RMQMessage

from summarizer import SummarizerPlugin


def main():
    print("Starting listener")

    # @Listener.RMQMessageCallback
    # def callback(ch, method, message: RMQMessage, handle_nack: callable = None):
    #     print(" [x] Received %r" % message.payload)
    #     ch.basic_ack(delivery_tag=method.delivery_tag)

    # rmq_host = os.environ.get("RMQ_HOST", "localhost")
    # rmq_port = os.environ.get("RMQ_PORT", 5672)
    # rmq_user = os.environ.get("RMQ_USER")
    # rmq_pass = os.environ.get("RMQ_PASS")
    # rmq_queue = os.environ.get("RMQ_QUEUE")
    # rmq_exchange = os.environ.get("RMQ_EXCHANGE")
    # rmq_routing_key = os.environ.get("RMQ_ROUTING_KEY")

    # connect_params = pika.ConnectionParameters(
    #     host=rmq_host,
    #     port=rmq_port,
    #     credentials=pika.PlainCredentials(rmq_user, rmq_pass),
    # )
    # type_config = Listener.ListenerTypeConfig(
    #     queue=rmq_queue,
    #     exchange_name=rmq_exchange,
    #     exchange_type="topic",
    #     routing_key=rmq_routing_key,
    # )
    # listener = Listener(connect_params, type_config)
    # listener.on_message(message_callback=callback)

    summarizer = SummarizerPlugin(model="CNNDM-uncased")
    print(
        summarizer.summarize(
            [
                """The team said that AGI has the potential to give everyone incredible new capabilities. “We can imagine a world where all of us have access to help with almost any cognitive task, providing a great force multiplier for human ingenuity and creativity.OpenAI also hinted at the flaws of its existing methodologies in achieving AGI. The team said: Of course, our current progress could hit a wall, but we can articulate the principles we care about most – i.e. maximizing the good and minimising the bad; access to, and governance of AGI to be widely and fairly shared; and navigating massive risks. """
            ],
            0.2,
        )
    )


if __name__ == "__main__":
    main()
