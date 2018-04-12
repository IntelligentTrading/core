import logging
from unixtimestampfield.fields import UnixTimeStampField

from django.db import models
from apps.strategy.models.strategy import Strategy

logger = logging.getLogger(__name__)


class BackTest(models.Model):
    '''
    for each backtest run we have one record in db with results data
    '''

    timestamp = UnixTimeStampField(null=False)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)  # id of a strategy Strategy Table
    strategy_name = models.CharField(max_length=32, null=False, blank=False)

    backtested_performance = models.FloatField(null=True)

    def __init__(self, strategy):
        self.strategy = strategy


    def run_backtest_one_curency_pair(self, counter_currency, transaction_currency):
        gain_to_counter_currency = None
        gain_to_random_strategy = None

        return gain_to_counter_currency, gain_to_random_strategy


    def run_backtest_portfolio(self):
        pass