import logging
from apps.TA import TAException
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.subscriber import TASubscriber, timestamp_is_near_5min, get_nearest_5min_timestamp
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
    def query(cls, ticker, exchange="", key="", key_suffix="",
              timestamp=None, periods=0, index="",
              *args, **kwargs):

        if index:
            key_suffix = f'{index}:' + key_suffix

        results_dict = super().query(key=key, key_prefix="", key_suffix=key_suffix,
                                     timestamp=timestamp, periods=periods,
                                     *args, **kwargs)

        results_dict['index'] = index
        return results_dict



class PriceSubscriber(TASubscriber):

    classes_subscribing_to = [
        PriceVolumeHistoryStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        # parse timestamp from data
        # f'{data_history.ticker}:{data_history.exchange}:{data_history.timestamp}'
        [ticker, exchange, timestamp] = data.split(":")


        if not timestamp_is_near_5min(timestamp):
            return
        else:
            logger.debug("near to a 5 min time marker")

        timestamp = get_nearest_5min_timestamp(timestamp)

        price = PriceStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)
        index_values = {}

        for index in defualt_price_indexes:
            logger.debug(f'process price for ticker: {ticker}')

            # example key = "XPM_BTC:poloniex:PriceVolumeHistoryStorage:close_price"
            sorted_set_key = f'{ticker}:{exchange}:PriceVolumeHistoryStorage:{index}'

            index_values[index] = [
                float(db_value.decode("utf-8").split(":")[0])
                for db_value
                in self.database.zrangebyscore(sorted_set_key, timestamp - 300, timestamp + 45)
            ]

            try:

                if not len(index_values[index]):
                    price.value = None
                elif index == "open_price":
                    price.value = index_values["open_price"][0]
                elif index == "close_price":
                    price.value = index_values["close_price"][-1]
                elif index == "low_price":
                    price.value = min(index_values["low_price"])
                elif index == "high_price":
                    price.value = max(index_values["high_price"])

            except IndexError:
                pass  # couldn't find a useful value
            except ValueError:
                pass  # couldn't find a useful value
            else:
                if price.value:
                    price.index = index
                    price.save()
                    logger.info("saved new thing: " + price.get_db_key())

        all_values_set = (
                set(index_values["open_price"]) |
                set(index_values["close_price"]) |
                set(index_values["low_price"]) |
                set(index_values["high_price"])
        )

        if not len(all_values_set):
            return

        for index in derived_price_indexes:
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
                price.index = index
                price.save(publish=True)
