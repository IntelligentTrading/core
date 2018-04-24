from django.test import TestCase

#from apps.indicator.models import Price
#from apps.channel.models.exchange_data import SOURCE_CHOICES

#from settings import SOURCE_CHOICES

from apps.api.views.tickers import group_items



class TestPriceV1APITests(TestCase):


    def test_group_source_and_counter_currency(self):

        source_items = [
            {
                "counter_currency": 0,
                "transaction_currency": "ANT",
                "source": 0
            },
            {
                "counter_currency": 0,
                "transaction_currency": "ANT",
                "source": 1
            },
            {
                "counter_currency": 0,
                "transaction_currency": "ANT",
                "source": 2
            },
            {
                "counter_currency": 1,
                "transaction_currency": "ANT",
                "source": 1
            },
            {
                "counter_currency": 0,
                "transaction_currency": "EMC",
                "source": 1
            },
            {
                "counter_currency": 0,
                "transaction_currency": "EMC",
                "source": 1
            },
            {
                "counter_currency": 0,
                "transaction_currency": "EMC",
                "source": 2
            },
            {
                "counter_currency": 2,
                "transaction_currency": "OMG",
                "source": 1
            },
            
        ]
        print(group_items(source_items))
        #self.assertEqual(group_items(source_items), {'EMC': {'counter_currency': [0], 'source': [1, 2]}, 'ANT': {'counter_currency': [0, 1], 'source': [0, 1, 2]}, 'OMG': {'counter_currency': [2], 'source': [1]}})
 