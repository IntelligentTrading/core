import os
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from TA import logger


deployment_type = os.environ.get('DEPLOYMENT_TYPE', 'LOCAL')


app = Flask(__name__)
api = Api(app)
logger.info("Flask app instantiated.")


# todo: if env == "PRODUCTION":
#     run scheduler for cleanup of


# ROUTING
from TA.resources.historical_data import HistoricalDataAPI
api.add_resource(HistoricalDataAPI, '/api/historical_data/<string:ticker>')
logger.info("Flask API resource added: /api/historical_data/<string:ticker>")

from TA.resources.price_volume import PriceVolumeAPI
api.add_resource(PriceVolumeAPI, '/api/price_volume/<string:ticker>')
logger.info("Flask API resource added: /api/price_volume/<string:ticker>")

logger.info("Flask resources and routes are ready.")


# REGISTER WORKERS
@app.cli.command()
def worker():
    from TA.worker import work
    work()
