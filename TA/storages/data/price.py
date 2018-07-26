import logging
from abc import ABC

from TA.api import database
from TA.storages.abstract.indicator import IndicatorStorage
from TA.storages.data.pv_history import PriceVolumeHistoryStorage, defualt_price_indexes, derived_price_indexes
from TA.worker import WorkerException


class PriceException(WorkerException):
    pass


class TASubscriber(ABC):

    def __init__(self):
        from TA.worker import redis_client
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe(PriceVolumeHistoryStorage.describer_class)

    def __call__(self):
        data_event = self.pubsub.get_message()
        if not data_event:
            return
        if not data_event.get('type') == 'message':
            return

        # data_event = {
        #   'type': 'message',
        #   'pattern': None,
        #   'channel': b'channel',
        #   'data': b"dude, what's up?"
        # }

        try:
            self.say_something_im_giving_up_on_you(data_event['channel'], data_event['data'])
        except KeyError:
            pass  # message not in expected format. just ignore
        except Exception as e:
            raise WorkerException(str(e))


    def say_something_im_giving_up_on_you(self, channel, data):
        if not channel == PriceVolumeHistoryStorage.describer_class:
            return

        # parse timestamp from data
        # f'{data_history.ticker}:{data_history.exchange}:{data_history.timestamp}'
        [ticker, exchange, timestamp] = data.split(":")

        # close to a five minute period mark? (+ or - 45 seconds)
        seconds_from_five_min = int(timestamp) + 45 % 300
        if seconds_from_five_min < 90:
            # we are close to a 5 min marker
            # resample history to save prices for last 5 min

            price = PriceStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)
            index_values = {}

            for index in defualt_price_indexes:

                # example key = "XPM_BTC:poloniex:PriceVolumeHistoryStorage:close_price"
                sorted_set_key = f'{ticker}:{exchange}:PriceVolumeHistoryStorage:{index}'

                index_values[index] = [
                    float(db_value.decode("utf-8").split(":")[0])
                    for db_value
                    in database.zrangebyscore(sorted_set_key, timestamp-300, timestamp)
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
                    while len(all_values_set) > 2:
                        values.remove(max(values_set))
                        values.remove(min(values_set))
                    price.value = values_set.pop()

                elif index == "mean_price":
                    price.value = sum(values_set) / (len(values_set) or 1)

                elif index == "price_variance":
                    # this is too small of a period size to measure variance
                    pass

                if price.value:
                    price.index = index
                    price.save()


class PriceStorage(IndicatorStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close_price")
        self.value = kwargs.get('value')


    def save(self, pipeline=None):

        # meets basic requirements for saving
        if not all(self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp):
            logging.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceException("save error, missing data")

        if not self.force_save:
            if not self.index in defualt_price_indexes:
                logging.error("price index not in approved list, raising exception...")
                raise PriceException("unknown index")

        self.db_key_suffix = ":{index}".format(self.index)
        return super().save(pipeline=pipeline)


values = set([
    float(db_value.decode("utf-8").split(":")[0])
    for db_value
    in database.zrangebyscore(key, timestamp - 300, timestamp)
])
while len(values) > 2:
    values.remove(max(values))
    values.remove(min(values))

for first_item in values: break

print(first_item)