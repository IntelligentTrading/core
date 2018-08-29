import os
import logging
from abc import ABC
import pika
import redis
from apps.TA import deployment_type

SIMULATED_ENV = deployment_type == "LOCAL"
# todo: use this to mark keys in redis db, so they can be separated and deleted

logger = logging.getLogger('redis_db')

if deployment_type == "LOCAL":
    REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    database = redis.Redis(connection_pool=pool)
else:
    database = redis.from_url(os.environ.get("REDIS_URL"))

logger.info("Redis connection established for app database.")

# hold this in python memory for fast access
# todo: does this even work with namespaces??
set_of_known_sets_in_redis = set()


class PubSub(ABC):

    def __init__(self, topic: str):
        self.topic = topic
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.topic)

    def send(self, message: str):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.topic,
                                   body=message)
        print(" [x] Sent 'Hello World!'")

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    def receive(self):
        self.channel.basic_consume(self.callback,
                                   queue=self.topic,
                                   no_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

with PubSub("hello") as pubsub:
    pubsub.send("yo")
