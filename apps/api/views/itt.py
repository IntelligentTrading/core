import ccxt
import urllib.request, json

from cache_memoize import cache_memoize

from rest_framework.views import APIView
from rest_framework.response import Response


class ITTPriceView(APIView):
    """Return ITT price

    /api/v2/itt
    """

    def get(self, request, format=None):
#        return Response(get_itt_token_price())
        return Response(get_itt_token_price_from_ryptocompare_com())


# Helpers methods

# Cache for 2 hours.
@cache_memoize(2*60*60)
def get_itt_token_price_from_ryptocompare_com():
    with urllib.request.urlopen("https://min-api.cryptocompare.com/data/pricemulti?fsyms=ITT&tsyms=BTC,USD") as url:
        data = json.loads(url.read().decode())
    return {'symbol': 'ITT/USD', 'close': data['ITT']['USD']}


# Cache for 8 hours.
@cache_memoize(8*60*60)
def get_itt_token_price():
    minimum_itt_price = 0.001

    ccap = ccxt.coinmarketcap()
    itt = ccap.fetch_ticker('ITT/USD')

    if itt['close'] < minimum_itt_price:
        itt_close = minimum_itt_price
    else:
        itt_close = itt['close']
    return {'symbol': 'ITT/USD', 'close': itt_close, 'quoteVolume': itt['quoteVolume'], 'datetime': itt['datetime']}
