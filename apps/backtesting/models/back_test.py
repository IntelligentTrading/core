import logging
from unixtimestampfield.fields import UnixTimeStampField
from django.db import models
from apps.indicator.models.price_resampl import PriceResampl
from apps.signal.models import Signal
from apps.signal.models.signal import ALL_SIGNALS
from datetime import datetime
from enum import Enum
from settings import COUNTER_CURRENCY_CHOICES
import numpy as np

logger = logging.getLogger(__name__)

class BacktestStatus(Enum):
    OK = 'OK'
    PRICE_ERROR = 'PR_ERR'

START_CASH = 1000


class BackTest(models.Model):
    '''
    This is a log of all backtesting runs.
    For each backtest run we have one record in db with resulted metrics
    '''

    # starting time of backtesting
    timestamp = UnixTimeStampField(null=False)

    # strategy name
    strategy_class_name = models.CharField(max_length=64, null=False)

    # start of time period being backtested
    start_timeframe = UnixTimeStampField(null=False)

    # end of time period being backtested
    end_timeframe = UnixTimeStampField(null=False)

    # transaction currency
    transaction_currency = models.CharField(max_length=6, null=False, blank=False)

    # counter currency
    counter_currency = models.SmallIntegerField(null=False)

    # source exchange
    source = models.SmallIntegerField(null=False)

    # resample period
    resample_period = models.PositiveSmallIntegerField(null=False)

    # profit percent to counter currency
    profit_percent = models.FloatField(null=True)

    # profit percent to counter currency with conversion of initial and end values to USDT
    profit_percent_USDT = models.FloatField(null=True)

    # number of trades
    num_trades = models.FloatField(null=True)

    # number of profitable trade pairs
    num_profitable_trade_pairs = models.FloatField(null=True)

    # avg profit percent per trade pair (buy, sell)
    avg_profit_per_trade_pair = models.FloatField(null=True)

    # number of buys
    num_buys = models.FloatField(null=True)

    # number of sells
    num_sells = models.FloatField(null=True)

    # buy and hold profit percent (buy on start_timeframe, get value on end_timeframe)
    buy_and_hold_profit_percent = models.FloatField(null=True)

    # buy and hold profit percent with conversion of start and end value to USDT
    buy_and_hold_profit_percent_USDT = models.FloatField(null=True)

    # percent gain of strategy compared to buying and holding
    percent_gain_over_buy_and_hold = models.FloatField(null=True)

    # percent gain of strategy compared to buying and holding in USDT
    percent_gain_over_buy_and_hold_USDT = models.FloatField(null=True)

    # calculation status
    status = models.CharField(max_length=6, null=False, blank=False)

    def __init__(self, strategy_class_object, timestamp, start_timeframe, end_timeframe):
        # see https://stackoverflow.com/questions/24537091/error-no-attribute-state
        super(BackTest, self).__init__()
        self.strategy_class_object = strategy_class_object
        self.start_timeframe = start_timeframe 
        self.end_timeframe = end_timeframe
        self.timestamp = timestamp

    def run_backtest_on_one_curency_pair(self, source, transaction_currency, counter_currency, resample_period):
        """
        Backtests the strategy given in the class constructor for one currency pair on one exchanger.
        :param source: exchanger ID
        :param transaction_currency: currency being traded
        :param counter_currency: counter currency
        :param resample_period: horizon information
        :return: True if any trades were made, False otherwise
        """

        # instantiate strategy object from class object
        strategy = self.strategy_class_object(transaction_currency=transaction_currency,
                                 counter_currency=counter_currency, source=source, timestamp=self.timestamp,
                                 resample_period=resample_period)
        self.strategy_class_name = str(strategy)

        # extract all strategy signals
        signals = strategy.get_all_signals_in_time_period(self.start_timeframe, self.end_timeframe)
        #TODO check is this ts is empty, no sence to continue if no signals are generated

        # simulate trading based on strategy signals
        dict = self.simulate_trading(signals, START_CASH, transaction_currency, counter_currency,
                                     self.start_timeframe, self.end_timeframe, resample_period, source)
        if dict is not None:
            self.create_row_and_save(dict)
        return dict is not None


    def run_backtest_on_several_currency_pairs(self):
        # allow moving all money into another currency
        # TODO: need signals from Alex to carry currency info
        pass


    def run_backtest_on_all_currency(self):
        """
        Backtests the strategy provided in the constructor on all currency pairs and all exchangers and
        computes aggregated statistics.
        """
        pass
        # in the current version, the looping over currency pairs is done in helpers.py

        # TODO: run the same for several-currency strategies


    def create_row_and_save(self, strategy_backtest_results):
        self.transaction_currency = strategy_backtest_results["transaction_currency"]
        self.counter_currency = strategy_backtest_results["counter_currency"]
        self.resample_period = strategy_backtest_results["resample_period"]
        self.source = strategy_backtest_results["source"]
        self.profit_percent = strategy_backtest_results["profit_percent"]
        self.profit_percent_USDT = strategy_backtest_results["profit_percent_USDT"]
        self.num_trades = strategy_backtest_results["num_trades"]
        self.num_profitable_trade_pairs = strategy_backtest_results["num_profitable_trades"]
        self.num_buys = strategy_backtest_results["num_buys"]
        self.num_sells = strategy_backtest_results["num_sells"]
        self.avg_profit_per_trade_pair = strategy_backtest_results["average_profit_percent_per_trade"]
        self.buy_and_hold_profit_percent = strategy_backtest_results["profit_buy_and_hold_percent"]
        self.buy_and_hold_profit_percent_USDT = strategy_backtest_results["profit_buy_and_hold_percent_USDT"]
        self.percent_gain_over_buy_and_hold = strategy_backtest_results["percent_gain_over_buy_and_hold"]
        self.percent_gain_over_buy_and_hold_USDT = strategy_backtest_results["percent_gain_over_buy_and_hold_USDT"]
        self.status = strategy_backtest_results["status"].value
        self.save()


    def run_backtest_portfolio(self):
        # allow holding several currencies at the same time (portfolio)
        pass

    # TODO: different transaction costs for different exchangers
    def simulate_trading(self, signals, start_cash, transaction_currency, counter_currency, start_timeframe,
                         end_timeframe, resample_period, source, transaction_cost_percent=0.0025):
        """
        Simulates trading with one currency based on signals.
        :param signals: a queryset of signals
        :param start_cash: starting amount of counter_currency
        :param transaction_currency: currency that we're buying
        :param counter_currency: our base currency
        :param start_timeframe: start of the time period that is being evaluated
        :param end_timeframe: end of the time period that is being evaluated
        :param resample_period: resample period (horizon)
        :param source: code of exchanger used
        :param transaction_cost_percent: exchanger fee per each trade
        :return: a dictionary with various stats if any trading takes place based on the signal list, None if the signal
                 list is empty or no trades get executed (for instance if only sell signals are in the list)
        """

        cash = start_cash   # the amount of counter_currency we have at any moment of trading
        crypto = 0          # the amount of transaction_currency we have at any moment of trading
        num_buys = 0        # total number of buys
        num_sells = 0       # total number of sells
        num_profitable_trades = 0   # total number of profitable trades (=number of sells for which we make a profit)
        invested_on_buy = 0         # the amount of cash spent on the last buy
        total_profit_percent_per_trade = 0    # average profit obtained by a buy-sell pair

        # convert start value to USDT (for performance statistics)
        start_cash_USDT = calculate_value_in_USDT(start_cash, start_timeframe,
                                                  counter_currency, source, resample_period)

        # store the time of the last trade
        last_trade_timestamp = None

        # simulate trading according to signals
        # we always spend all money to buy when a buy signal appears, and hold until the first sell signal
        for timestamp, signal in signals.items():
            last_trade_timestamp = timestamp  # storing the time of the last trade, needed for USDT conversion etc.

            price = get_resampl_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period)
            if price is None or price == 0:
                logger.error("Unable to find or interpolate price data or price is zero - highly unlikely, please investigate!")
                continue  # covers a very rare case when we don't have price data and can't interpolate either

            if indicates_sell(signal) and crypto > 0 and invested_on_buy > 0:
                cash = cash + execute_sell(crypto, price, transaction_cost_percent)
                crypto = 0
                num_sells += 1

                # how much did we make on this buy - sell pair (in percent)
                buy_sell_pair_profit_percent = (cash - invested_on_buy) / invested_on_buy
                invested_on_buy = 0  # reset the invested amount for the trade pair
                total_profit_percent_per_trade += buy_sell_pair_profit_percent

                # check if the trade was profitable
                if buy_sell_pair_profit_percent > 0:
                    num_profitable_trades += 1

            elif indicates_buy(signal) and cash > 0:
                invested_on_buy += cash
                crypto = crypto + execute_buy(cash, price, transaction_cost_percent)
                cash = 0
                num_buys += 1

        num_trades = num_buys + num_sells

        # What if we didn't trade at all? Happens when no signals, or only sell signals.
        if num_trades == 0:
            return None

        # housekeeping in case that the last signal was a buy signal, meaning we didn't end up with cash but with crypto
        # calculate the value of this crypto in counter_currency to estimate profit
        if crypto > 0:
            price = get_resampl_price_at_timepoint(datetime.utcfromtimestamp(end_timeframe), source,
                                                   transaction_currency, counter_currency, resample_period)
            if price is None:
                end_cash = None
                end_cash_USDT = None
            else:
                end_cash = execute_sell(crypto, price, transaction_cost_percent=0)  # simulate selling at the end of timeframe
                end_cash_USDT = calculate_value_in_USDT(end_cash, end_timeframe, counter_currency, source, resample_period)
        else:
            end_cash = cash
            end_cash_USDT = calculate_value_in_USDT(end_cash, last_trade_timestamp.timestamp(),
                                                    counter_currency, source, resample_period)

        # calculate statistics
        if end_cash is not None:
            profit = end_cash - start_cash
            profit_percent = profit / start_cash
        else:
            profit = None
            profit_percent = None

        average_profit_percent_per_trade = total_profit_percent_per_trade / num_trades
        profit_buy_and_hold = calculate_profit_buy_and_hold(start_cash, source, transaction_currency, counter_currency,
                                                            resample_period, start_timeframe, end_timeframe,
                                                            transaction_cost_percent)
        if profit_buy_and_hold is not None and profit is not None:
            profit_buy_and_hold_percent = profit_buy_and_hold / start_cash
            percent_gain_over_buy_and_hold = profit_percent - profit_buy_and_hold_percent
        else:
            profit_buy_and_hold_percent = None
            percent_gain_over_buy_and_hold = None

        if end_cash_USDT is not None and start_cash_USDT is not None:
            profit_USDT = end_cash_USDT - start_cash_USDT
            profit_percent_USDT = profit_USDT / start_cash_USDT
        else:
            profit_USDT = None
            profit_percent_USDT = None

        if counter_currency == 2:  # if already trading in USDT
            profit_buy_and_hold_USDT = profit_buy_and_hold
        else:
            profit_buy_and_hold_USDT = calculate_profit_buy_and_hold_USDT(start_cash, source, transaction_currency,
                                                                          counter_currency, resample_period, start_timeframe,
                                                                          end_timeframe, transaction_cost_percent)
        if profit_buy_and_hold_USDT is not None and profit_percent_USDT is not None and start_cash_USDT is not None:
            profit_buy_and_hold_percent_USDT = profit_buy_and_hold_USDT / start_cash_USDT
            percent_gain_over_buy_and_hold_USDT = profit_percent_USDT - profit_buy_and_hold_percent_USDT
        else:
            profit_buy_and_hold_percent_USDT = None
            percent_gain_over_buy_and_hold_USDT = None

        dict = {"transaction_currency": transaction_currency,
                "counter_currency": counter_currency,
                "source": source,
                "resample_period": resample_period,
                "profit": profit,
                "profit_percent": profit_percent,
                "profit_USDT": profit_USDT,
                "profit_percent_USDT": profit_percent_USDT,
                "num_buys": num_buys,
                "num_sells": num_sells,
                "num_trades": num_trades,
                "num_profitable_trades": num_profitable_trades,
                "average_profit_percent_per_trade": average_profit_percent_per_trade,
                "profit_buy_and_hold": profit_buy_and_hold,
                "profit_buy_and_hold_percent": profit_buy_and_hold_percent,
                "profit_buy_and_hold_USDT": profit_buy_and_hold_USDT,
                "profit_buy_and_hold_percent_USDT": profit_buy_and_hold_percent_USDT,
                "percent_gain_over_buy_and_hold": percent_gain_over_buy_and_hold,
                "percent_gain_over_buy_and_hold_USDT": percent_gain_over_buy_and_hold_USDT}
        status = BacktestStatus.PRICE_ERROR if None in dict.values() else BacktestStatus.OK
        dict["status"] = status
        return dict


# checks if a signal indicates sell
def indicates_sell(signal_name):
    return ALL_SIGNALS[signal_name].trend == -1


# checks if a signal indicates buy
def indicates_buy(signal_name):
    return ALL_SIGNALS[signal_name].trend == 1


# calculates how much currency we can buy for a given amount of cash and given the transaction costs
def execute_buy(cash_amount, unit_price, transaction_cost_percent):
    return cash_amount * (1 - transaction_cost_percent) / unit_price


# calculates how much we earn by selling a given amount of currency and given the transaction costs
def execute_sell(crypto_amount, unit_price, transaction_cost_percent):
    return crypto_amount * unit_price * (1 - transaction_cost_percent)


# calculates the profit if buying the currency on start_timeframe and selling on end_timeframe
def calculate_profit_buy_and_hold(cash, source, transaction_currency, counter_currency,
                                  resample_period, start_timeframe, end_timeframe, transaction_cost_percent):

    start_price = get_resampl_price_at_timepoint(datetime.utcfromtimestamp(start_timeframe),
                                                 source, transaction_currency, counter_currency, resample_period)
    end_price = get_resampl_price_at_timepoint(datetime.utcfromtimestamp(end_timeframe),
                                               source, transaction_currency, counter_currency, resample_period)

    if start_price is None or end_price is None:
        return None

    # buying at the start of timeframe for all cash
    crypto = execute_buy(cash, start_price, transaction_cost_percent)

    # selling everything at the end of timeframe
    end_cash = execute_sell(crypto, end_price, transaction_cost_percent)

    return end_cash - cash


# calculates the profit if buying the currency on start_timeframe and selling on end_timeframe, in USDT
def calculate_profit_buy_and_hold_USDT(cash, source, transaction_currency, counter_currency,
                                  resample_period, start_timeframe, end_timeframe, transaction_cost_percent):

    if counter_currency == 2:
        return calculate_profit_buy_and_hold(cash, source, transaction_currency, counter_currency,
                                  resample_period, start_timeframe, end_timeframe, transaction_cost_percent)

    # convert cash value to USDT
    cash_USDT = calculate_value_in_USDT(cash, start_timeframe, counter_currency, source, resample_period)
    if cash_USDT is None:
        return None

    # buying at the start of timeframe for all cash
    start_price = get_resampl_price_at_timepoint(datetime.utcfromtimestamp(start_timeframe),
                                                 source, transaction_currency, counter_currency, resample_period)
    if start_price is None:
        return None

    crypto = execute_buy(cash, start_price, transaction_cost_percent)

    # selling everything at the end of timeframe
    end_price = get_resampl_price_at_timepoint(datetime.utcfromtimestamp(end_timeframe),
                                               source, transaction_currency, counter_currency, resample_period)
    if end_price is None:
        return None

    end_cash = execute_sell(crypto, end_price, transaction_cost_percent)

    # convert end cash value to USDT
    end_cash_USDT = calculate_value_in_USDT(end_cash, end_timeframe, counter_currency, source, resample_period)
    if end_cash_USDT is None:
        return None

    return end_cash_USDT - cash_USDT


# calculates the value of counter_currency amount in USDT on a given timestamp
def calculate_value_in_USDT(amount, timestamp, counter_currency, source, resample_period):
    value = None
    if counter_currency == 2:   # trivial case, if the value is already in USDT
        return amount
    else:
        price_USDT = get_resampl_price_at_timepoint(timestamp=datetime.utcfromtimestamp(timestamp), source=source,
                                                    transaction_currency=get_currency_name(counter_currency),
                                                    counter_currency=2, resample_period=resample_period)
        if price_USDT is not None:  # if no data for USDT price, None will be returned
            value = amount * price_USDT
    return value


# finds all distinct tuples (source, transaction_currency, counter_currency for which we have signals
# between start_timeframe and end_timeframe
def get_distinct_trading_pairs(start_timeframe, end_timeframe):
    distinct = Signal.objects.filter(
        timestamp__gte=start_timeframe,
        timestamp__lte=end_timeframe)\
        .values("source", "transaction_currency", "counter_currency").distinct()
    return distinct


# retrieves currency name from id, e.g. 0 = "BTC"
def get_currency_name(currency_id):
    for id, name in COUNTER_CURRENCY_CHOICES:
        if id == currency_id:
            return name



# temporary fix to contain backtesting in this file until Pandas interpolation bug is fixed
# using old version of get_price_at_timepoint
def get_resampl_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period):
    price_at_timepoint = PriceResampl.objects.filter(
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        source=source,
        resample_period=resample_period,
        timestamp=timestamp
    ).values('mean_price').order_by('timestamp').first()

    if price_at_timepoint is not None and price_at_timepoint['mean_price'] is not None:
        return price_at_timepoint['mean_price']

    # we don't have exact price data
    # extract first earlier price that is not null
    last_price_before = PriceResampl.objects.filter(
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        source=source,
        resample_period=resample_period,
        timestamp__lte=timestamp,
        mean_price__isnull=False
    ).values('timestamp', 'mean_price').order_by('-timestamp').first()  # largest timestamp smaller than timestamp

    # extract first later price that is not null
    first_price_after = PriceResampl.objects.filter(
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        source=source,
        resample_period=resample_period,
        timestamp__gte=timestamp,
        mean_price__isnull=False
    ).values('timestamp', 'mean_price').order_by('timestamp').first()  # smallest timestamp larger than timestamp

    # three cases: (1) we have only left price point, (2) we have only right price point and (3) we have both
    if first_price_after is None:           # (1) if we don't have data for the price after timestamp
        if last_price_before is not None:   # if there's data for the price before, we return that
            return last_price_before['mean_price']
        else:
            logger.error("Unable to interpolate price data.")   # otherwise, we can't estimate price
            return None
    elif last_price_before is None:             # (2) if we don't have data for the price before timestamp
        return first_price_after['mean_price']  # we checked before that first_price_after is not None, so return that

    else:  # (3) we have two price points, before and after timestamp, interpolation can be done
        timestamp_before = last_price_before['timestamp']
        price_before = last_price_before['mean_price']
        timestamp_after = first_price_after['timestamp']
        price_after = first_price_after['mean_price']

        interpolated_price = np.interp(x=timestamp.timestamp(),
                                       xp=[timestamp_before.timestamp(), timestamp_after.timestamp()],
                                       fp=[price_before, price_after])
        return interpolated_price

