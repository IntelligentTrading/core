import logging
import json
import boto3
import pandas as pd
from datetime import datetime
from SNSEventHandler import AbstractSNSEventHandler, ContextException
(BUY, SELL, IGNORE) = (1,-1,0)


class StrategyException(Exception):
    pass


class AbstractStrategyHandler(AbstractSNSEventHandler):
    """
    `indicators` are the data points used for making trade get_signal
    the `signal` is the buy, sell, or ignore result from this trade strategy
    """

    timestamp = None
    source = None
    resample_period = None
    transaction_currency = None
    counter_currency = None

    indicators = []
    strategy_indicators_set = None
    indicator_now_set = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sns_publish_topic_prefix += "strategy-"

        self.indicators = []
        self.timestamp = kwargs.get('timestamp', datetime.now())
        self.source = kwargs.get('source')
        self.resample_period = kwargs.get('resample_period')
        self.transaction_currency = kwargs.get('transaction_currency')
        self.counter_currency = kwargs.get('counter_currency')
        self._parameters = kwargs


    def run(self):
        if not self.sns_context:
            raise ContextException("sns_context is empty or missing!")
        self.make_signal()
        if "signal" not in self.results:
            raise StrategyException("strategy is missing a signal!")
        elif self.results["signal"] in [BUY, SELL, IGNORE]:
            raise StrategyException("non-standard signal! use one of these" +
                                    "BUY, SELL, IGNORE = 1,-1,0")
        else:
            self.emit_sns_message(self.results)


    def save(self):
        # TODO
        # everything run as expected?
        # anything unexpcted to log?
        # did results get saved or sent correctly?
        # no silent bugs or errors?
        if not self.sns_client_response:
            if self.signal in [BUY, SELL]:
                raise StrategyException("Signal data created but never sent!")
            # if client response has error:
                # SNSMessageException("Error when sending signal. Signal not sent!")
        # ...
        # ...


    def make_signal(self):
        """
        for method overriding - insert business logic
        """
        self.signal = IGNORE
        return self.signal


    @property
    def results(self):
        return {
            "signal": self.signal,
            "transaction_currency": self.transaction_currency,
            "counter_currency": self.counter_currency,
            "signal_parameters": self._parameters,
         }


    def get_indicator(indicator_name):
        if indicator_name in self.indicators:
            return self.indicators[indicator_name]

        # logic here for query to collect indicator data


    def check_indicators_now(self)->set:
        # get all indicators emitted now
        current_indicators_set = get_all_indicators_names_now(**self.parameters)

        # check if any of them belongs to our strategy
        self.indicator_now_set = self.strategy_indicators_set.intersection(current_indicators_set)

        if len(self.indicator_now_set) > 1 :
            logging.warning(" Ouch... several indicators for one strategy at the same time... highly unlikely, please investigate!"
                            + str(self.indicator_now_set))

        # check if the previos indicator is the same, return None, i.e. if you bought something, do not buy it again
        prev_indicator = self.get_previous_indicator()
        #TODO

        return self.indicator_now_set


    def get_previous_indicator(self)->pd.Series:
        # get indicators quite far in a history
        tshift = 3600 * 24 * 20  # 20 days back
        previous_indicator = self.get_all_indicators_in_time_period(self.timestamp-tshift, self.timestamp).tail(1)
        return previous_indicator


    def get_all_indicators_in_time_period(self, start_timestamp, end_timestamp)->pd.Series:
        # get all indicators in prodived timeframe
        # TODO that method might be overriden in child class if we need more soficticated strategy rules
        # TODO need API call here
        all_indicators_ts = get_indicators_ts(start_timestamp, end_timestamp, **self.parameters)

        # filter out those not belonging to our strategy
        self.strategy_ts = all_indicators_ts[all_indicators_ts.isin(self.strategy_indicators_set)]
        return self.strategy_ts
