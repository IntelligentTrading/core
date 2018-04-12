from abc import ABC, abstractmethod

class AbstractStrategy(ABC):

    @abstractmethod
    def is_signal_now(self,timestamp):
        pass

    @abstractmethod
    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        pass

    @abstractmethod
    def print(self):
        '''
        word description of stragety here
        '''
        pass