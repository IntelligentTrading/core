import os
import sys
from abc import ABC
import pika


class RabbitMQ(ABC):

    def __init__(self, topic: str, exchange: str = "", exchange_type: str = ""):
        self.topic = topic
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.environ.get("RABBITMQ_URL", "localhost"))
        )
        self.channel = self.connection.channel()

        if exchange or exchange_type:
            self.channel.exchange_declare(exchange=exchange,
                                          exchange_type=exchange_type)
            result = self.channel.queue_declare(exclusive=True)
            self.queue_name = result.method.queue

        else:
            self.channel.queue_declare(queue=self.topic)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class WorkQueue(RabbitMQ):

    def add_task(self, message):
        message = ' '.join(sys.argv[1:]) or "Hello World!"
        self.channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=message)


class PubSub(RabbitMQ):

    def send(self, message: str):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.topic,
                                   body=message)


    def callback(ch, method, properties, body):

        print(" [x] Received %r" % body)

    def receive(self):
        self.channel.basic_consume(self.callback,
                                   queue=self.topic,
                                   no_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()


# with PubSub("hello") as pubsub:
#     pubsub.send("yo")
c

class Router(RabbitMQ):
    """
    https://www.rabbitmq.com/tutorials/tutorial-four-python.html
    For Receiving messages selectively
    """
    # todo: write implementation using example in url
    pass


class Topic(RabbitMQ):
    """
    https://www.rabbitmq.com/tutorials/tutorial-five-python.html
    Receiving messages based on a pattern (topics)
    """
    # todo: write implementation using example in url

    def __init__(self, ticker, *args, **kwargs):
        self.topic = f"*.ticker.*"
        super().__init__(self.topic, *args, **kwargs)


class RPC(RabbitMQ):
    """
    https://www.rabbitmq.com/tutorials/tutorial-six-python.html
    Remote procedure call (RPC) Request/reply pattern example
    """
    # todo: write implementation using example in url
    pass


