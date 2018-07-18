import logging
import json
import boto3
import requests
import pandas as pd
from datetime import datetime
from SNSEventHandler import AbstractSNSEventHandler, SNSEventException
from abc import abstractmethod

(BUY, SELL, IGNORE) = (1,-1,0)

# API_URL = "https://itt-core-stage.herokuapp.com/api"
# API_ENDPOINTS = {
#     "SMA": "/v2/sma/",
#     "RSI": "/v2/rsi/",
# }

API_URL = "https://dfpatoqdyk.execute-api.us-east-2.amazonaws.com/dev"
API_ENDPOINTS = {
    "SMA": "/mock_rsi",
    "RSI": "/mock_rsi",
}

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

    indicators = {}
    strategy_indicators_set = None
    indicator_now_set = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # the super constructor will process the SNS msg that triggered the function
        self.sns_publish_topic_prefix += "strategy-"

        # Below: parsing the raw SNS msg and filling all the info
        # assuming raw_sns_message exists, TODO: error handling if not
        # TODO: fill out transaction_currency, counter_currency etc. from here or from kwargs? think about it.

        json_msg = json.loads(self.raw_sns_message)

        self.indicators = json_msg.get('indicators', {})
        self.timestamp = json_msg.get('timestamp', datetime.now())
        self.source = json_msg.get('source')
        self.resample_period = json_msg.get('resample_period')
        self.transaction_currency = json_msg.get('transaction_currency')
        self.counter_currency = json_msg.get('counter_currency')
        self._parameters = kwargs


    def run(self):
        if not self.incoming_indicators_are_supported():
            raise SNSEventException("none of the incoming indicators recognized by this strategy!")

        if not self.sns_event:
            raise SNSEventException("sns_event is empty or missing!")

        self.make_signal()
        if "signal" not in self.results:
            raise StrategyException("strategy is missing a signal!")
        elif self.results["signal"] not in [BUY, SELL, IGNORE]:
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

    @property
    @abstractmethod
    def used_indicators(self):
        pass

    def incoming_indicators_are_supported(self):
        return len(set(self.used_indicators).intersection(set(self.indicators.keys()))) > 0


    def get_indicator(self, indicator_name):
        # this happens if the indicator we need was received in the incoming msg
        if indicator_name in self.indicators:
            return self.indicators[indicator_name]
        # else

        # if we're missing some of the indicators, pull them via API (e.g. a strategy invoked by one signal, dependent on several more)
        params = {'transaction_currency': self.transaction_currency,
                  'counter_currency': self.counter_currency}
        logging.info(params)
        response = requests.get(API_URL+API_ENDPOINTS[indicator_name], params=params)
        logging.info(response.url)
        try:
            self.indicators[indicator_name] = response.json()
        except:
            self.indicators[indicator_name] = {}
            logging.info(response)
        return self.indicators[indicator_name]

    #############################################################
    ####### I don't think we need any of the functions below
    ####### Or at least I don't see how they would be usable in an SNS-triggered architecture
    ##############################################################

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
