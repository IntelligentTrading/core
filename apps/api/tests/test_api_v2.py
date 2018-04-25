import json
from dateutil.parser import parse

from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework import status

from settings import EXCHANGE_MARKETS, COUNTER_CURRENCIES



class APIv2Tests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v2'

    def get_content(self, url): # helper method
        response = self.client.get(url)
        assert(response.status_code == status.HTTP_200_OK)
        return json.loads(response.content)


    def test_itt_api(self):
        url = self.url
        content = self.get_content(f"{url}/itt/")
        self.assertEqual(list(content.keys()), ['symbol', 'close', 'quoteVolume', 'datetime'])
        self.assertEqual(content['symbol'], 'ITT/USD')
        self.assertTrue(content['close'] > 0.001)
        self.assertTrue(content['quoteVolume'] > 1)
        self.assertTrue(parse(content['datetime']))

    def test_tickers_api(self):
        url = f"{self.url}/tickers"
        # exchanges
        content = self.get_content(f"{url}/exchanges/")
        self.assertTrue(len(content) > 2)
        self.assertEqual(tuple(content), EXCHANGE_MARKETS)

        # counter-currencies
        content = self.get_content(f"{url}/counter-currencies/")
        self.assertEqual(len(content), len(COUNTER_CURRENCIES))
        self.assertTrue({'symbol': 'BTC', 'index': 0, 'enabled': True} in content)
        self.assertTrue({'symbol': 'USDT', 'index': 2, 'enabled': True} in content)

        # transaction-currencies
        #content = self.get_content(f"{url}/transaction-currencies/")
