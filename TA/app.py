from flask import Flask, logging
from flask_restful import Resource, Api
import redis


REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
db = redis.Redis(connection_pool=pool)

app = Flask(__name__)
api = Api(app)


from TA.resources.price import PriceAPI
api.add_resource(PriceAPI, '/price')

