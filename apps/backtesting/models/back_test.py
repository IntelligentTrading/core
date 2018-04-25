import logging
import time
from unixtimestampfield.fields import UnixTimeStampField
from django.db import models
from apps.strategy.models.rsi_sma_strategies import *
from apps.backtesting.models.order import Order, OrderType
from apps.indicator.models.price_resampl import get_price_at_timepoint

logger = logging.getLogger(__name__)


class BackTest(models.Model):
    '''
    This is a log of all backtesting runs.
    For each backtest run we have one record in db with resulted metrics
    '''

    timestamp = UnixTimeStampField(null=False)
    strategy_class_name = models.CharField(max_length=64, null=True)

    # TODO: @Karla, please add as many metrics as you need with their appropriate names
    profit_percent = models.FloatField(null=True)
    profit_percent_USDT = models.FloatField(null=True)
    num_trades = models.IntegerField(null=True)
    num_profitable_trades = models.IntegerField(null=True)
    avg_profit_per_trade = models.FloatField(null=True)
    buy_and_hold_profit_percent = models.FloatField(null=True)
    buy_and_hold_profit_percent_USDT = models.FloatField(null=True)
    num_sells = models.IntegerField(null=True)


    # gain_to_counter_currency, gain_to_random_strategy etc


    def __init__(self, strategy_class_name, start_timeframe, end_timeframe):
        # see https://stackoverflow.com/questions/24537091/error-no-attribute-state
        super(BackTest, self).__init__()

        self.strategy_class_name = str(strategy_class_name).split(".")[-1][:-2]
        self.start_timeframe = start_timeframe
        self.end_timeframe = end_timeframe
        self.evaluate_profit_on_last_order = True


    def run_backtest_on_one_curency_pair(self, source, transaction_currency, counter_currency, resample_period):
        # TODO:
        # - get a starting amount of currency ( 1 BTC? )
        # - get all strategy signals by calling RsiSimpleStrategy.get_all_signals_in_time_period(..)
        # - run your buy/sells on this signals
        # - you will need to implement a get_price_at_timepoint function in price_resample model
        # NOTE: get timestamps from returned signals!! they are keys in DB!!!
        # - save the resulted metrics in self.backtested_performance_1
        # - make sure it is saved as a separate record in BackTest DB table


        strategy = RsiSimpleStrategy(transaction_currency=transaction_currency, counter_currency=counter_currency,
                                     source=source, timestamp=self.timestamp, resample_period=resample_period)

        signals = strategy.get_all_signals_in_time_period(self.start_timeframe, self.end_timeframe)
        self.start_cash = 1
        self.start_crypto = 0
        self.timestamp = time.time()
        orders, _ = self.get_orders(signals, self.start_cash, self.start_crypto,
                                    transaction_currency, counter_currency, resample_period)
        self.profit_percent, self.num_trades, self.num_profitable_trades, \
          self.avg_profit_per_trade_pair, self.num_sells = self.execute_orders(orders)



    def run_backtest_on_several_currency_pairs(self):
        # allow moving all money into another currency
        pass


    def run_backtest_on_all_currency(self):
        resample_period = 60
        logger.info("BACKTEST on all start")
        # iterate over all currencies and exchangers (POLONIEX etc) with run_backtest_on_one_curency_pair
        atomic_tuples = [ (0, 'BTC', 2), (0, 'ETH', 0)] # generate all triples you need (source/transact_curr/counter_curr)
        for source, transaction_currency, counter_currency in atomic_tuples:
            self.run_backtest_on_one_curency_pair(source, transaction_currency, counter_currency, resample_period)
            pass

        # run the same for several-currenciy strategies
        return False

    def indicates_buy(self, signal):
        assert len(signal) == 1
        if "_buy" or "_bull" in signal[0]:
            return True
        else:
            return False

    def indicates_sell(self, signal):
        assert len(signal) == 1
        if "_sell" or "_bear" in signal[0]:
            return True
        else:
            return False


    def run_backtest_portfolio(self):
        # allow holding several currencies at the same time (portfolio)
        pass


    def get_orders(self, signals, start_cash, start_crypto, transaction_currency, counter_currency,
                    resample_period=60, source=0, transaction_cost_percent=0.0025):
        orders = []
        order_signals = []
        cash = start_cash
        crypto = start_crypto
        buy_currency = None
        for timestamp, signal in signals.items():
            price = get_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period)
            if price is None:
                continue
            if self.indicates_sell(signal) and crypto > 0: # and signal.transaction_currency == buy_currency:
                order = Order(OrderType.SELL, transaction_currency, counter_currency,
                                    timestamp, crypto, price, transaction_cost_percent)
                orders.append(order)
                order_signals.append(signal)
                delta_crypto, delta_cash = order.execute()
                cash = cash + delta_cash
                crypto = crypto + delta_crypto
                assert crypto == 0
            elif self.indicates_buy(signal) and cash > 0:
                buy_currency = transaction_currency
                order = Order(OrderType.BUY, transaction_currency, counter_currency,
                                    timestamp, cash, price, transaction_cost_percent)
                orders.append(order)
                order_signals.append(signal)
                delta_crypto, delta_cash = order.execute()
                cash = cash + delta_cash
                crypto = crypto + delta_crypto
                assert cash == 0

        return orders, order_signals


    def execute_orders(self, orders):
        cash = self.start_cash
        crypto = self.start_crypto
        num_trades = 0
        num_profitable_trades = 0
        invested_on_buy = 0
        avg_profit_per_trade_pair = 0
        num_sells = 0

        for i, order in enumerate(orders):
            if i == 0: # first order
                assert order.order_type == OrderType.BUY
                buy_currency = order.transaction_currency

            delta_crypto, delta_cash = order.execute()
            cash += delta_cash
            crypto += delta_crypto
            num_trades += 1
            if order.order_type == OrderType.BUY:
                invested_on_buy = -delta_cash
                buy_currency = order.transaction_currency
            else:
                # the currency we're selling must match the bought currency
                assert order.transaction_currency == buy_currency
                num_sells += 1
                buy_sell_pair_profit_percent = (delta_cash - invested_on_buy) / invested_on_buy * 100
                avg_profit_per_trade_pair += buy_sell_pair_profit_percent
                if buy_sell_pair_profit_percent > 0:
                    num_profitable_trades += 1

        if num_sells != 0:
            avg_profit_per_trade_pair /= num_sells

        if self.evaluate_profit_on_last_order and num_trades > 0:
            end_price = orders[-1].unit_price
        else: # TODO
            if num_trades == 0:
                print("WARNING: no orders were generated by the chosen strategy.")
            try:
                if num_trades > 0:
                    end_price = get_price(buy_currency, self.end_time, self.counter_currency)
                else:
                    end_price = get_price(self.start_crypto_currency, self.end_time, self.counter_currency)

            except:
                print("WARNING: no data found for end price.")
                end_price = -1

        end_cash = cash
        end_crypto = crypto
        end_crypto_currency = buy_currency if num_trades > 0 else self.start_crypto_currency

        profit = (end_price*end_crypto + end_cash) - self.start_cash
        profit_percent = profit / self.start_cash * 100
        return profit_percent, num_trades, num_profitable_trades, avg_profit_per_trade_pair, num_sells


    def orders_from_signals(self, signals):
        for signal_type in signals:
            if "buy" or "bull" in signal_type:
                order = Order(OrderType.BUY)


