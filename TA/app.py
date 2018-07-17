from flask import Flask, logging
from flask_restful import reqparse, abort, Api, Resource
import redis


REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
db = redis.Redis(connection_pool=pool)
logging.info("Redis connection established.")


app = Flask(__name__)
api = Api(app)
logging.info("Flask app instantiated.")


# ROUTING
from TA.resources.price import PriceAPI
api.add_resource(PriceAPI, '/price/<ticker>')




logging.info("Flask resources and routes are ready.")
