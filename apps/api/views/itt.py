import ccxt
from cache_memoize import cache_memoize

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.api.permissions import RestAPIPermission



class ITTPriceView(APIView):
    """Return ITT price

    /api/v2/itt
    """

    permission_classes = (RestAPIPermission, )

    def get(self, request, format=None):
        return Response(get_itt_token_price())


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
