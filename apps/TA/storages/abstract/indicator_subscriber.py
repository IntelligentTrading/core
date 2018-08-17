from apps.TA.storages.abstract.indicator import IndicatorException
from apps.TA.storages.abstract.ticker_subscriber import TickerSubscriber, get_nearest_5min_timestamp
from settings import logger



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

        score = str(data["score"])
        [value, timestamp] = data["name"].split(":")

        if not timestamp == data["score"]:
            logger.warning(f'Unexpected that score in name {timestamp} '
                           f'is different than score {score}')

        self.value = value
        self.timestamp = int(float(timestamp))

        if not self.timestamp == get_nearest_5min_timestamp(self.timestamp):
            raise IndicatorException("indicator timestamp should be 5min timestamp")

        return


    def handle(self, channel, data, *args, **kwargs):
        self.extract_params(channel, data, *args, **kwargs)
