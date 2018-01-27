from datetime import datetime
import time
import simplejson as json
from google.cloud import datastore
from apps.bot.telegram.utilities import telegram_command


# @telegram_command("cryptocompare_price", pass_args=True)
# def cryptocompare_price(args):
#     #todo: refactor to use data_sources and datastore
#     return get_price(",".join(args).upper(), "USD,BTC")
#
# cryptocompare_price.help_text = "get the price for any crypto ticker eg. ETH"


@telegram_command("price", pass_args=True)
def price(args):
    try:
        symbol = args[0].upper()

        client = datastore.Client()
        query = client.query(kind='Indicators')
        query.add_filter('symbol', '=', symbol)
        query.order = ['-timestamp']
        datastore_entity = list(query.fetch(limit=1))[0]
        price_satoshis = datastore['value']

        return "\n".join([
            symbol + " Price",
            "BTC {:,.8f}".format(price_satoshis / 100000000),
            "as of %ds ago, Poloniex" % int(time.time() - datastore['timestamp'])
        ])

    except Exception as e:
        print(str(e))
        return "Please check the name of coin. Coin not found!"

price.help_text = "get the BTC price for any coin eg. /price ETH"


def get_last_price(symbol, channel="Poloniex"):
    """
    get latest price from datastore
    :param symbol: "ETH"
    :param channel: "Poloniex"
    :return: integere price in satoshis
    """

    # query database for latest price data
    client = datastore.Client()
    query = client.query(kind='Indicators')
    query.add_filter('symbol', '=', symbol)
    query.add_filter('ilk', '=', 'price')
    query.order = ['-timestamp']
    datastore_entity = list(query.fetch(limit=1))[0]

    # datastore entity example
    # {'ilk': 'price',
    # 'symbol': symbol,
    # 'value': int(price_data['last'] * 8),  # satoshis
    # 'timestamp': timestamp,
    # 'channel': channel,
    #  }

    return datastore_entity['value']


def get_last_price_humanized(symbol):
    return "BTC {:,.8f}".format(get_last_price(symbol)/100000000)
