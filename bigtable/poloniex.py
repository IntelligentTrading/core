""" Intelligent Trading Poloniex Worker
"""
import json
import time

from requests import get, RequestException
from input_data import input_data


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

            if col_f == "BTC":
                aux_dict["data"]["BTC"]["%s_LAST" % aux] = "%s" % data[aux]['last']
                aux_dict["data"]["BTC"]["%s_CHANGE" % aux] = "%s" % data[aux]['percentChange']
                aux_dict["data"]["BTC"]["%s_HIGH" % aux] = "%s" % data[aux]['high24hr']
                aux_dict["data"]["BTC"]["%s_LOW" % aux] = "%s" % data[aux]['low24hr']
                aux_dict["data"]["BTC"]["%s_VOLUME" % aux] = "%s" % data[aux]['baseVolume']

            if col_f == "USDT":
                aux_dict["data"]["USDT"]["%s_LAST" % aux] = "%s" % data[aux]['last']
                aux_dict["data"]["USDT"]["%s_CHANGE" % aux] = "%s" % data[aux]['percentChange']
                aux_dict["data"]["USDT"]["%s_HIGH" % aux] = "%s" % data[aux]['high24hr']
                aux_dict["data"]["USDT"]["%s_LOW" % aux] = "%s" % data[aux]['low24hr']
                aux_dict["data"]["USDT"]["%s_VOLUME" % aux] = "%s" % data[aux]['baseVolume']

            if col_f == "XMR":
                aux_dict["data"]["XMR"]["%s_LAST" % aux] = "%s" % data[aux]['last']
                aux_dict["data"]["XMR"]["%s_CHANGE" % aux] = "%s" % data[aux]['percentChange']
                aux_dict["data"]["XMR"]["%s_HIGH" % aux] = "%s" % data[aux]['high24hr']
                aux_dict["data"]["XMR"]["%s_LOW" % aux] = "%s" % data[aux]['low24hr']
                aux_dict["data"]["XMR"]["%s_VOLUME" % aux] = "%s" % data[aux]['baseVolume']

            if col_f == "ETH":
                aux_dict["data"]["ETH"]["%s_LAST" % aux] = "%s" % data[aux]['last']
                aux_dict["data"]["ETH"]["%s_CHANGE" % aux] = "%s" % data[aux]['percentChange']
                aux_dict["data"]["ETH"]["%s_HIGH" % aux] = "%s" % data[aux]['high24hr']
                aux_dict["data"]["ETH"]["%s_LOW" % aux] = "%s" % data[aux]['low24hr']
                aux_dict["data"]["ETH"]["%s_VOLUME" % aux] = "%s" % data[aux]['baseVolume']

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


if __name__ == '__main__':
    print(poloniex(debug=True))
