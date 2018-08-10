import logging
from apps.TA import TAException, PERIODS_4HR
from apps.TA.storages.abstract.ticker import TickerStorage
from apps.TA.storages.abstract.timeseries_storage import TimeseriesException


logger = logging.getLogger(__name__)


class IndicatorException(TAException):
    pass


class IndicatorStorage(TickerStorage):
    """
    stores indicators in a sorted set unique to each ticker and exchange
    requires data to be a resampling to represent the most recent 5min block of time
    timestamp value must be evenly divisible by 5 minutes (300 seconds)
    add short, medium, long as 1hr, 4hr, 24hr time horizons
    """
    class_describer = "indicator"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_describer = kwargs.get('class_describer', self.__class__.class_describer)

        # ALL INDICATORS ARE ASSUMED 5-MIN PERIOD RESAMPLED
        if self.unix_timestamp % 300 != 0:
            raise TimeseriesException("indicator timestamp should be % 300")
        # self.resample_period = 300  # 5 min

        self.horizon = int(kwargs.get('horizon', 1))
        self.periods = int(kwargs.get('periods', 1*self.horizon))

        if self.periods // self.horizon == 0:
            raise IndicatorException(f'horizon {self.horizon} '
                                     f'must be less than periods {self.periods} (or ==1)')
        elif self.periods % self.horizon != 0:
            raise IndicatorException(f'horizon {self.horizon} '
                                     f'must be a factor of periods {self.periods}')

        self.db_key_suffix = f':{self.periods}'


    @classmethod
    def query(cls, *args, **kwargs):

        periods_key = kwargs.get("periods_key", "")
        key_suffix = kwargs.get("key_suffix", "")

        if periods_key:
            kwargs["key_suffix"] = f'{periods_key}' + (f':{key_suffix}' if key_suffix else "")

        results_dict = super().query(*args, **kwargs)

        results_dict['periods_key'] = periods_key
        return results_dict


"""
===== EXAMPLE USAGE =====

my_indicator = TimeseriesIndicator(ticker="ETH_BTC",
                                   exchange="BITTREX",
                                   timestamp=1483228800)
my_indicator.value = "BUY BITCOIN"
my_indicator.save()

# advanced:

very_special_signal = TimeseriesIndicator(class_describer="SuperSignal",
                                          key="SuperSignal",
                                          key_suffix="answer_to_the_universe",
                                          ticker="ETH_BTC",
                                          timestamp=1483228800
                                          )
from settings.redis_db import database
pipeline = database.pipeline()
for thing in ['towel', 42, 'babelfish', 'vogon poetry']:
    very_special_signal.unix_timestamp += 300
    very_special_signal.value = thing
    pipeline = very_special_signal.save(pipeline)
pipeline.execute()

===== EXAMPLE USAGE =====
"""
