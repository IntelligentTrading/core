import logging
from apps.TA import TAException
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.subscriber import TickerSubscriber, timestamp_is_near_5min, get_nearest_5min_timestamp
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, defualt_price_indexes, derived_price_indexes

logger = logging.getLogger(__name__)


class PriceException(TAException):
    pass


class PriceStorage(IndicatorStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close_price")
        self.value = kwargs.get('value')
        self.db_key_suffix = f':{self.index}'

    def save(self, *args, **kwargs):

        # meets basic requirements for saving
        if not all([self.ticker, self.exchange,
                    self.index, self.value,
                    self.unix_timestamp]):
            logger.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceException("save error, missing data")

        if not self.force_save:
            if not self.index in defualt_price_indexes + derived_price_indexes:
                logger.error("price index not in approved list, raising exception...")
                raise PriceException("unknown index")

        self.db_key_suffix = f':{self.index}'
        return super().save(*args, **kwargs)

    @classmethod
    def query(cls, *args, **kwargs):

        if kwargs.get("periods_key", None):
            raise PriceException("periods_key is not usable in PriceStorage query")

        key_suffix = kwargs.get("key_suffix", "")
        index = kwargs.get("index", "")

        if index:
            kwargs["key_suffix"] = f'{index}' + (f':{key_suffix}' if key_suffix else "")

        results_dict = super().query(*args, **kwargs)

        results_dict['index'] = index
        return results_dict


class PriceSubscriber(TickerSubscriber):
    classes_subscribing_to = [
        PriceVolumeHistoryStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        # parse data like...
        # {
        #     "key": "POLY_BTC:binance:PriceVolumeHistoryStorage:open_price",
        #     "name": "3665:1533884227",
        #     "score": "1533884227"
        # }

        [ticker, exchange, object_class, index] = data["key"].split(":")
        if not object_class == channel == PriceVolumeHistoryStorage.__name__:
            logger.warning(f'Unexpected that these are not the same:'
                           f'object_class: {object_class}, '
                           f'channel: {channel}, '
                           f'subscribing class: {PriceVolumeHistoryStorage.__name__}')
        [value, name_score] = data["name"].split(":")
        score = data["score"]
        if not score == data["score"]:
            logger.warning(f'Unexpected that score in name {name_score} '
                           f'is different than score {score}')

        timestamp = int(float(score))

        if not timestamp_is_near_5min(timestamp):
            return
        else:
            logger.debug("near to a 5 min time marker")

        timestamp = get_nearest_5min_timestamp(timestamp)

        price = PriceStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)

        logger.debug(f'process price for ticker: {ticker} and index: {index}')

        # key_format = f'{ticker}:{exchange}:PriceVolumeHistoryStorage:{index}'
        sorted_set_key = data["key"]

        query_results = PriceVolumeHistoryStorage.query(
            ticker=ticker, exchange=exchange,
            index=index, timestamp=timestamp,
            periods_range=1, timestamp_tolerance=29
        )

        logger.debug("results from PriceVolumeHistoryStorage query... ")
        logger.debug(query_results)

        index_values = [int(v) for v in query_results['values']]
        # timestamps = [int(v) for v in query_results['timestamps']]

        try:
            if not len(index_values):
                price.value = None
            elif index == "open_price":
                price.value = index_values[0]
            elif index == "close_price":
                price.value = index_values[-1]
            elif index == "low_price":
                price.value = min(index_values)
            elif index == "high_price":
                price.value = max(index_values)

        except IndexError:
            pass  # couldn't find a useful value
        except ValueError:
            pass  # couldn't find a useful value
        else:
            if price.value:
                price.index = index
                price.save()
                logger.info("saved new thing: " + price.get_db_key())

        if index == "close_price":
            all_values_set = set(index_values)
            for other_index in ["open_price", "low_price", "high_price"]:
                query_results = PriceVolumeHistoryStorage.query(
                    ticker=ticker, exchange=exchange,
                    index=other_index, timestamp=timestamp,
                    periods_range=1, timestamp_tolerance=29
                )

                index_values = [int(v) for v in query_results['values']]

            all_values_set = all_values_set | set(index_values)

            if not len(all_values_set):
                return

            for index in derived_price_indexes:
                price.index = index
                price.value = None

                values_set = all_values_set.copy()

                if index == "midpoint_price":
                    while len(values_set) > 2:
                        values_set.remove(max(values_set))
                        values_set.remove(min(values_set))
                    price.value = values_set.pop()

                elif index == "mean_price":
                    price.value = sum(values_set) / (len(values_set) or 1)

                elif index == "price_variance":
                    # this is too small of a period size to measure variance
                    pass

                if price.value:
                    price.value = int(price.value)
                    price.index = str(index)
                    price.save(publish=True)
