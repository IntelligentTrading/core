import logging
from unixtimestampfield.fields import UnixTimeStampField
from django.db import models

logger = logging.getLogger(__name__)


class BackTest(models.Model):
    '''
    This is a log of all backtesting runs.
    For each backtest run we have one record in db with resulted metrics
    '''

    timestamp = UnixTimeStampField(null=False)
    strategy_class_name = models.CharField(max_length=64, null=True)

    # TODO: @Karla, please add as many metrics as you need with their appropriate names
    # feel free to rename
    backtested_performance_1 = models.FloatField(null=True)
    backtested_performance_2 = models.FloatField(null=True)
    # gain_to_counter_currency, gain_to_random_strategy etc


    def __init__(self, strategy_class_name, start_timeframe, end_timeframe):
        self.strategy_class_name = strategy_class_name


    def run_backtest_on_one_curency_pair(self, source, transaction_currency, counter_currency ):
        # TODO:
        # - get a starting amount of currency ( 1 BTC? )
        # - get all strategy signals by calling RsiSimpleStrategy.get_all_signals_in_time_period(..)
        # - run your buy/sells on this signals
        # - you will need to implement a get_price_at_timepoint function in price_resample model
        # NOTE: get timestamps from returned signals!! they are keys in DB!!!
        # - save the resulted metrics in self.backtested_performance_1
        # - make sure it is saved as a separate record in BackTest DB table

        self.backtested_performance_1 = None
        self.backtested_performance_2 = None


    def run_backtest_on_several_currency_pairs(self):
        # allow moving all money into another currency
        pass


    def run_backtest_on_all_currency(self):
        # iterate over all currencies and exchangers (POLONIEX etc) with run_backtest_on_one_curency_pair
        atomic_tuples = [ (0, 'BTC', 2), (0, 'ETH', 0)] # generate all triples you need (source/transact_curr/counter_curr)
        for source, transaction_currency, counter_currency in atomic_tuples:
            self.run_backtest_on_one_curency_pair(self, source, transaction_currency, counter_currency)
            pass

        # run the same for several-currenciy strategies
        return False


    def run_backtest_portfolio(self):
        # allow holding several currencies at the same time (portfolio)
        pass