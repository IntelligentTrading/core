import copy

from django.test import TestCase

from apps.api.helpers import get_source_index, get_itt_token_price
from apps.api.helpers import group_items, get_counter_currency_index, replace_exchange_code_with_name



class TestPriceV1APITests(TestCase):

    def setUp(self):
        self.source_items = [{'counter_currency': 0, 'source': 0, 'transaction_currency': 'ANT'}, {'counter_currency': 0, 'source': 1, 'transaction_currency': 'ANT'}, {'counter_currency': 0, 'source': 2, 'transaction_currency': 'ANT'}, {'counter_currency': 1, 'source': 1, 'transaction_currency': 'ANT'}, {'counter_currency': 0, 'source': 1, 'transaction_currency': 'EMC'}, {'counter_currency': 0, 'source': 1, 'transaction_currency': 'EMC'}, {'counter_currency': 0, 'source': 2, 'transaction_currency': 'EMC'}, {'counter_currency': 2, 'source': 1, 'transaction_currency': 'OMG'}]

    def test_group_source_and_counter_currency(self):
        grouped = group_items(self.source_items, key='transaction_currency', group_by=['source'])
        self.assertTrue({'transaction_currency': 'OMG', 'source': [1]} in grouped)
        self.assertTrue({'transaction_currency': 'ANT', 'source': [0, 1, 2]} in grouped)
        self.assertTrue({'transaction_currency': 'EMC', 'source': [1, 2]} in grouped)
        self.assertEqual(len(grouped), 3)

        grouped = group_items(self.source_items, key='transaction_currency', group_by=['source', 'counter_currency'])
        self.assertTrue({'counter_currency': [2], 'source': [1], 'transaction_currency': 'OMG'} in grouped)
        self.assertTrue({'counter_currency': [0, 1], 'source': [0, 1, 2], 'transaction_currency': 'ANT'} in grouped)
        self.assertTrue({'counter_currency': [0], 'source': [1, 2], 'transaction_currency': 'EMC'} in grouped)

    def test_get_counter_currency_index(self):
        self.assertEqual(get_counter_currency_index('BTC'), 0)
        self.assertEqual(get_counter_currency_index('USDT'), 2)

    def test_replace_exchange_code_with_name(self):
        source_items = copy.deepcopy(self.source_items)
        replaced = replace_exchange_code_with_name(source_items)
        self.assertEqual(replaced, [{'transaction_currency': 'ANT', 'exchange': 'poloniex', 'counter_currency': 0}, {'transaction_currency': 'ANT', 'exchange': 'bittrex', 'counter_currency': 0}, {'transaction_currency': 'ANT', 'exchange': 'binance', 'counter_currency': 0}, {'transaction_currency': 'ANT', 'exchange': 'bittrex', 'counter_currency': 1}, {'transaction_currency': 'EMC', 'exchange': 'bittrex', 'counter_currency': 0}, {'transaction_currency': 'EMC', 'exchange': 'bittrex', 'counter_currency': 0}, {'transaction_currency': 'EMC', 'exchange': 'binance', 'counter_currency': 0}, {'transaction_currency': 'OMG', 'exchange': 'bittrex', 'counter_currency': 2}])

    def test_get_source_index(self):
        self.assertEqual(get_source_index('poloniex'), 0)
        self.assertEqual(get_source_index('binance'), 2)

    def test_get_itt_token_price(self):
        itt = get_itt_token_price()
        self.assertTrue(itt['close']>0.001)
        self.assertEqual(sorted(list(itt.keys())), ['close', 'datetime', 'quoteVolume', 'symbol'])