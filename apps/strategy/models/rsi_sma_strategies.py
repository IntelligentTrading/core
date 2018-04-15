from apps.strategy.models.abstract_strategy import AbstractStrategy
from apps.signal.models.signal import ALL_SIGNALS, get_all_signals_names_now
import logging
logger = logging.getLogger(__name__)

class RsiSimpleStrategy(AbstractStrategy):
    '''
    select a subset of already generated signals from the Signal class
    that subset shall represent a given strategy, for example for RsiSimple  as follows:
    - RSI simple strategy is buy when RSI < 25 and sell when RSI > 85
    '''

    # list of signals belonging to this strategy
    # NOTE: check signals.ALL_SIGNALS namedtuple
    strategy_signals_set = set(['rsi_sell_3', 'rsi_buy_3'])

    def check_signal_now(self):
        # get all signals emitted now
        current_signals_set = get_all_signals_names_now(**self.parameters)

        # check if any of them belongs to our strategy
        final_set = self.strategy_signals_set.intersection(current_signals_set)

        if len(final_set) > 1 :
            logger.error(" Ouch... several signals for one strategy at the same time... highly unlikely, please investigate!")

        return final_set


    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        # return in a form of time/signal name
        pass



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