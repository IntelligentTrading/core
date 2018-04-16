from apps.strategy.models.abstract_strategy import AbstractStrategy
from apps.signal.models.signal import get_all_signals_names_now, get_signals_ts


import logging
logger = logging.getLogger(__name__)

################ Pattern for other strategies  #################
class RsiSimpleStrategy(AbstractStrategy):
    '''
    select a subset of already generated signals from the Signal class
    that subset shall represent a given strategy, for example for RsiSimple  as follows:
    - RSI simple strategy is buy when RSI < 25 and sell when RSI > 85
    '''

    # list of signals belonging to this strategy
    # NOTE: check signals.ALL_SIGNALS namedtuple
    strategy_signals_set = set(['rsi_sell_3', 'rsi_buy_3'])

    def check_signals_now(self):
        # get all signals emitted now
        current_signals_set = get_all_signals_names_now(**self.parameters)

        # check if any of them belongs to our strategy
        strategy_signal_set = self.strategy_signals_set.intersection(current_signals_set)

        if len(strategy_signal_set) > 1 :
            logger.error(" Ouch... several signals for one strategy at the same time... highly unlikely, please investigate!")

        return strategy_signal_set


    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        # get all signals in prodived timeframe
        all_signals_ts = get_signals_ts(start_timestamp, end_timestamp, **self.parameters)

        # filter out those not belonging to our strategy
        strategy_ts = all_signals_ts[all_signals_ts in self.strategy_signals_set]
        return

####################################



class SmaCrossOverStrategy(AbstractStrategy):
    strategy_signals_set = set() # add here

    def check_signal_now(self):
        pass


    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        pass



class RsiSmaMixedStrategy(AbstractStrategy):
    def check_signal_now(self):
        pass

    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        pass