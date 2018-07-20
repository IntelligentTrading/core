import logging
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import redis

logger = logging.getLogger('flask_api')
logger.setLevel(logging.DEBUG)

class TAException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)

class SuchWowException(TAException):
    def __init__(self, message):
        self.message = message
        such_wow = "==============SUCH=====WOW==============="
        logger.debug(f'\n\n{such_wow}\n\n{message}\n\n{such_wow}')


REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
db = redis.Redis(connection_pool=pool)
logger.info("Redis connection established.")


app = Flask(__name__)
api = Api(app)
logger.info("Flask app instantiated.")


# ROUTING
from TA.resources.price import PriceAPI
api.add_resource(PriceAPI, '/api/data_history')

from TA.resources.resampled import PriceVolumeResampledAPI
api.add_resource(PriceVolumeResampledAPI, '/api/resampled/<string:ticker>')


logger.info("Flask resources and routes are ready.")
