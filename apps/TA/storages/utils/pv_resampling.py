import logging

from apps.TA.storages.abstract.ticker_subscriber import get_nearest_5min_score
from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
from apps.TA.storages.data.price import PriceStorage
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, derived_price_indexes
from apps.TA.storages.data.volume import VolumeStorage

logger = logging.getLogger(__name__)


def generate_pv_storages(ticker: str, exchange: str, index: str, score: float) -> bool:
    score = get_nearest_5min_score(score)
    timestamp = TimeseriesStorage.timestamp_from_score(score)

    if "price" in index:
        storage = PriceStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)
    elif "volume" in index:
        storage = VolumeStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)
    else:
        raise Exception("I don't know what kind of index this is")

    logger.debug(f'process price for ticker: {ticker} and index: {index}')

    # eg. key_format = f'{ticker}:{exchange}:PriceVolumeHistoryStorage:{index}'

    query_results = PriceVolumeHistoryStorage.query(
        ticker=ticker, exchange=exchange,
        index=index, timestamp=timestamp,
        periods_range=1, timestamp_tolerance=29
    )

    logger.debug("results from PriceVolumeHistoryStorage query... ")
    logger.debug(query_results)

    try:
        index_values = [int(v) for v in query_results['values']]
        # timestamps = [int(v) for v in query_results['timestamps']]

        if not len(index_values):
            storage.value = None
        elif index == "close_volume":
            storage.value = index_values[-1]
        elif index == "open_price":
            storage.value = index_values[0]
        elif index == "low_price":
            storage.value = min(index_values)
        elif index == "high_price":
            storage.value = max(index_values)
        elif index == "close_price":
            storage.value = index_values[-1]
        else:
            raise IndexError("unknown index)")

    except IndexError:
        pass  # couldn't find a useful value or index (sorry for using this for both definitions of "index")
    except ValueError:
        pass  # couldn't find a useful value
    else:
        if storage.value:
            storage.index = index
            storage.save(publish=False)
            logger.info("saved new thing: " + storage.get_db_key())

    if index == "close_price":
        all_values_set = set(index_values)  # these are the close prices
        for other_index in ["open_price", "low_price", "high_price"]:
            query_results = PriceVolumeHistoryStorage.query(
                ticker=ticker, exchange=exchange,
                index=other_index, timestamp=timestamp,
                periods_range=1, timestamp_tolerance=29
            )

            index_values = [int(v) for v in query_results['values']]

        all_values_set = all_values_set | set(index_values)

        if not len(all_values_set):
            return False

        price_storage = PriceStorage(ticker=ticker, exchange=exchange, timestamp=timestamp)

        for index in derived_price_indexes:
            price_storage.index = index
            price_storage.value = None

            values_set = all_values_set.copy()

            if index == "midpoint_price":
                while len(values_set) > 2:
                    values_set.remove(max(values_set))
                    values_set.remove(min(values_set))
                price_storage.value = values_set.pop()

            elif index == "mean_price":
                price_storage.value = sum(values_set) / (len(values_set) or 1)

            elif index == "price_variance":
                # this is too small of a period size to measure variance
                pass

            if price_storage.value:
                price_storage.value = int(price_storage.value)
                price_storage.index = str(index)
                price_storage.save(publish=bool(index == "close_price"))

    return True
