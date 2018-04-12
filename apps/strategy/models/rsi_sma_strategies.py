from apps.strategy.models.abstract_strategy import AbstractStrategy

class RsiSimpleStrategy(AbstractStrategy):
    '''
    select a subset of already generated signals from the Signal class
    that subset shall represent a given strategy, for example for RsiSimple  as follows:
    - RSI simple strategy is buy when RSI < 25 and sell when RSI > 85
    '''
    @staticmethod
    def is_signal_now(timestamp):
        # check if now there are any on RSI<25 and RSI>85
        # return a signal_id (?) if any
        pass

    @staticmethod
    def get_all_signals_in_time_period(start_timestamp, end_timestamp):
        pass



class SmaCrossOverStrategy(AbstractStrategy):
    @staticmethod
    def is_signal_now( timestamp):
        pass

    @staticmethod
    def get_all_signals_in_time_period(start_timestamp, end_timestamp):
        pass



class RsiSmaMixedStrategy(AbstractStrategy):
    def is_signal_now(self, timestamp):
        pass

    def get_all_signals_in_time_period(self, start_timestamp, end_timestamp):
        pass