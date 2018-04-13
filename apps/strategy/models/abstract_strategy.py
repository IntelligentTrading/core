from abc import ABC, abstractmethod

class AbstractStrategy(ABC):
    timestamp = None
    source = None
    resample_period = None

    transaction_currency = None
    counter_currency = None


    def __init__(self, parameters):
        self.timestamp = parameters['timestamp']
        self.source = parameters['source']
        self.resample_period = parameters['resample_period']
        self.transaction_currency = parameters['transaction_currency']
        self.counter_currency = parameters['counter_currency']


    def is_signal_now(self):
        pass


    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        pass


    def print(self):
        '''
        word description of stragegy here
        '''
        description = " word description"
        return description

