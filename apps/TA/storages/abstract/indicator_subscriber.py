from apps.TA.storages.abstract.indicator import IndicatorException, IndicatorStorage
from apps.TA.storages.abstract.ticker_subscriber import TickerSubscriber, get_nearest_5min_timestamp
from settings import logger


class IndicatorSubscriber(TickerSubscriber):
    class_describer = "indicator_subscriber"
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

        [value, score] = data["name"].split(":")
        self.value, self.score = float(value), float(score)

        if not self.score == int(float(data["score"])):
            logger.warning(f'Unexpected that score in name {self.score} '
                           f'is different than score {data["score"]}')

        if not self.score == int(self.score):
            raise IndicatorException("indicator timestamp should be 5min timestamp, score should be whole number (int)")

        self.timestamp = IndicatorStorage.timestamp_from_score(self.score)

        return


    def pre_handle(self, channel, data, *args, **kwargs):
        self.extract_params(channel, data, *args, **kwargs)
        super().pre_handle(channel, data, *args, **kwargs)
