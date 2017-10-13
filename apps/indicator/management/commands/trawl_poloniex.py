import logging
import datetime as dt

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")




        logger.info("All done.")


import json
import time

from requests import get, RequestException

def poloniex(debug=None):
    """ Poloniex Worker

    Args:
        debug: if True enable debug mode, default is None

    Returns:
        The key of the new row
    """
    try:
        req = get('https://poloniex.com/public?command=returnTicker')
        data = req.json()
        timestamp = int(time.time())
        row_key = 'poloniex#%s' % timestamp

        aux_dict = dict()
        aux_dict["row_key"] = "{0}".format(row_key)
        aux_dict["data"] = dict()

        aux_dict["data"]["BTC"] = dict()
        aux_dict["data"]["USDT"] = dict()
        aux_dict["data"]["XMR"] = dict()
        aux_dict["data"]["ETH"] = dict()

        for aux in sorted(data):
            col_f = aux.split('_')[0]
            last = int(float(data[aux]['last']) * 10 ** 8)
            volume = int(float(data[aux]['last']) * 10 ** 8)

            if col_f == "BTC":
                aux_dict["data"]["BTC"]["%s_LAST" % aux] = last
                aux_dict["data"]["BTC"]["%s_VOLUME" % aux] = volume

            if col_f == "USDT":
                aux_dict["data"]["USDT"]["%s_LAST" % aux] = last
                aux_dict["data"]["USDT"]["%s_VOLUME" % aux] = volume

            if col_f == "XMR":
                aux_dict["data"]["XMR"]["%s_LAST" % aux] = last
                aux_dict["data"]["XMR"]["%s_VOLUME" % aux] = volume

            if col_f == "ETH":
                aux_dict["data"]["ETH"]["%s_LAST" % aux] = last
                aux_dict["data"]["ETH"]["%s_VOLUME" % aux] = volume

        if debug is True:
            print(json.dumps(aux_dict, sort_keys=True, indent=4))

        query = input_data(project_id='optimal-oasis-170206',
                           instance_id='itt-develop',
                           table_id='channels',
                           data=aux_dict)

        if query is True:
            pass
        else:
            return 'Error: {0}'.format(query)

    except RequestException:
        return 'Error to collect data from Poloniex'

    return "New row: {0}".format(row_key)
