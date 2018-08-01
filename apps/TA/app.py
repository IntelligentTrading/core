import os
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import logging

logger = logging.getLogger(__name__)


app = Flask(__name__)
api = Api(app)
logger.info("Flask app instantiated.")


# todo: if env == "PRODUCTION":
#     run scheduler for cleanup of


# ROUTING
from apps.TA.resources.historical_data import HistoricalDataAPI
api.add_resource(HistoricalDataAPI, '/api/historical_data/<string:ticker>')
logger.info("Flask API resource added: /api/historical_data/<string:ticker>")

from apps.TA.resources.price_volume import PriceVolumeAPI
api.add_resource(PriceVolumeAPI, '/api/price_volume/<string:ticker>')
logger.info("Flask API resource added: /api/price_volume/<string:ticker>")

logger.info("Flask resources and routes are ready.")

