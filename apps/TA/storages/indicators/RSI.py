import logging
from apps.TA.storages.abstract.indicator import IndicatorStorage


class RSI(IndicatorStorage):

    relative_strength = None

    @property
    def rsi(self):  # relative strength index
        # rsi = 100 - 100 / (1 + rUp / rDown)
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))
        else:
            return None

    def compute_rs(self)->float:
        '''
        Relative Strength calculation.
        The RSI is calculated a a property, we only save RS
        (RSI is a momentum oscillator that measures the speed and change of price movements.)
        :return:
        '''

        resampl_price_df = price_resampl.get_n_last_resampl_df(
            20 * self.resample_period,
            self.source, self.transaction_currency, self.counter_currency, self.resample_period
        )

        resampl_close_price_ts = resampl_price_df.close_price
        logging.debug('RSI: current period=' + str(self.resample_period) + ', close prices available for that period=' + \
                     str(resampl_close_price_ts.size))

        if (resampl_close_price_ts is not None) and (resampl_close_price_ts.size > 12):
            # difference btw start and close of the day, remove the first NA
            delta = resampl_close_price_ts.diff()
            delta = delta[1:]

            up, down = delta.copy(), delta.copy()
            up[up < 0] = 0
            down[down > 0] = 0

            # Calculate the 14 period back EWMA for each up/down trends
            # QUESTION: shall this 14 perid depends on period 15,60, 360?
            roll_up = up.ewm(com = 14, min_periods=3).mean()
            roll_down = np.abs(down.ewm(com = 14, min_periods=3).mean())

            rs_ts = roll_up / roll_down

            self.relative_strength = float(rs_ts.tail(1))  # get the last element for the last time point
            return self.relative_strength
        else:
            logging.debug(':RSI was not calculated:: Not enough closing prices')
            logging.debug \
                ('     current period=' + str(self.resample_period) + ', close prices available for that period=' + str
                    (resampl_close_price_ts.size) )
            return None
