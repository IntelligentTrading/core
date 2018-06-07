import logging
import time


from apps.strategy.models.strategy_ref import get_all_strategy_classes
from apps.backtesting.models.back_test import get_distinct_trading_pairs
from apps.backtesting.models.back_test import BackTest

from settings import PERIODS_LIST



logger = logging.getLogger(__name__)

def _backtest_all_strategies():

    now_timestamp = time.time()

    # get all strategies in the system from Strategies model
    strategies_class_list = get_all_strategy_classes()

    # TODO: decide which period we're going to use
    time_end = time.time()
    time_start = time_end - 3600 * 24 * 60  # a month back

    # get all triplets (source, transaction_currency, counter_currency)
    trading_pairs = get_distinct_trading_pairs(time_start, time_end)

    # run reavaluation
    for strategy_class in strategies_class_list:
        # begin = time.time()
        strategy_class_name = strategy_class.__name__

        # iterate over all currencies and exchangers (POLONIEX etc) with run_backtest_on_one_curency_pair
        logger.info("Started backtesting {} on all currency...".format(strategy_class_name))

        for resample_period in PERIODS_LIST:
            for trading_pair in trading_pairs:
                back_test_run = BackTest(strategy_class, now_timestamp, time_start, time_end)

                if back_test_run.run_backtest_on_one_curency_pair(trading_pair["source"],
                                                                  trading_pair["transaction_currency"],
                                                                  trading_pair["counter_currency"],
                                                                  resample_period):

                    # save only if there were backtesting results
                    back_test_run.save()

        logger.info("Ended backtesting {} on all currency.".format(strategy_class_name))
        # end = time.time()
        # logger.info("Time to test strategy {}: {} minutes".format(strategy_class_name, (end-begin)/60))
