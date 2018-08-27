from apps.TA.storages.abstract.indicator import IndicatorException
from apps.TA.storages.abstract.ticker_subscriber import TickerSubscriber, get_nearest_5min_timestamp
from settings import logger
import numpy as np


class IndicatorSubscriber(TickerSubscriber):

    classes_subscribing_to = [
        # ...
    ]

    def extract_params(self, channel, data, *args, **kwargs):

        # parse data like...
        # {
        #     "key": "VEN_USDT:binance:PriceStorage:close_price",
        #     "name": "176760000:1532373300",
        #     "score": "1532373300"
        # }

        [self.ticker, self.exchange, object_class, self.key_suffix] = data["key"].split(":")

        if not object_class == channel and object_class in [
            sub_class.__name__ for sub_class in self.classes_subscribing_to
        ]:
            logger.warning(f'Unexpected that these are not the same:'
                           f'object_class: {object_class}, '
                           f'channel: {channel}, '
                           f'subscribing classes: {self.classes_subscribing_to}')

        [value, timestamp] = data["name"].split(":")
        self.value = float(value)
        self.timestamp = int(float(timestamp))

        if not self.timestamp == int(float(data["score"])):
            logger.warning(f'Unexpected that score in name {self.timestamp} '
                           f'is different than score {data["score"]}')

        if not self.timestamp == get_nearest_5min_timestamp(self.timestamp):
            raise IndicatorException("indicator timestamp should be 5min timestamp")

        return


    def pre_handle(self, channel, data, *args, **kwargs):
        self.extract_params(channel, data, *args, **kwargs)
        super().pre_handle(channel, data, *args, **kwargs)


    @staticmethod
    def get_values_array_from_query(query_results, limit=0):

        value_array = [float(v) for v in query_results['values']]

        if limit:
            if not isinstance(limit, int) or limit < 1:
                raise IndicatorException(f"bad limit: {limit}")

            elif len(value_array) > limit:
                value_array = value_array[-limit:0]

        return np.array(value_array)
