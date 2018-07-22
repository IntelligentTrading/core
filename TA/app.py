import os
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


# SIMULATED_ENV = os.get("env", "TEMP")
# todo: use this to mark keys in redis db, so they can be separated and deleted
REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
# todo: change db=1,2,3 for stage/prod/test envs?
database = redis.Redis(connection_pool=pool)
logger.info("Redis connection established.")
set_of_known_sets_in_redis = set()


app = Flask(__name__)
api = Api(app)
logger.info("Flask app instantiated.")

# if env == "PRODUCTION":
#     run scheduler for cleanup of





# ROUTING
from TA.resources.historical_data import HistoricalDataAPI
api.add_resource(HistoricalDataAPI, '/api/historical_data/<string:ticker>')

from TA.resources.price_volume import PriceVolumeAPI
api.add_resource(PriceVolumeAPI, '/api/price_volume/<string:ticker>')


logger.info("Flask resources and routes are ready.")
