from abc import ABC, abstractmethod
from apps.signal.models.signal import get_all_signals_names_now, get_signals_ts

import logging
logger = logging.getLogger(__name__)

class AbstractStrategy(ABC):
    timestamp = None
    source = None
    resample_period = None
    transaction_currency = None
    counter_currency = None

    parameters = None
    strategy_signals_set = None
    signal_now_set = None


    def __init__(self, **parameters):
        self.timestamp = parameters['timestamp']
        self.source = parameters['source']
        self.resample_period = parameters['resample_period']
        self.transaction_currency = parameters['transaction_currency']
        self.counter_currency = parameters['counter_currency']

        self.parameters = parameters


    def check_signals_now(self):
        # get all signals emitted now
        current_signals_set = get_all_signals_names_now(**self.parameters)

        # check if any of them belongs to our strategy
        self.signal_now_set = self.strategy_signals_set.intersection(current_signals_set)

        if len(self.signal_now_set) > 1 :
            logger.error(" Ouch... several signals for one strategy at the same time... highly unlikely, please investigate!")

        # check if the previos signal is the same, return None, i.e. if you bough something, do not buy it again
        prev_signal = self.get_previous_signal()

        return self.signal_now_set


    def get_previous_signal(self):
        # get signals quite fa in a history
        tshift = 3600 * 24 * 10  # 10 days back
        previous_signal = self.get_all_signals_in_time_period(self.timestamp-tshift, self.timestamp).tail(1)
        return previous_signal


    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        # get all signals in prodived timeframe
        all_signals_ts = get_signals_ts(start_timestamp, end_timestamp, **self.parameters)

        # filter out those not belonging to our strategy
        self.strategy_ts = all_signals_ts[all_signals_ts in self.strategy_signals_set]
        return self.strategy_ts



