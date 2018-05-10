# Signal folder
For now only contains a Signal model which is in essence a log of all emitted signals to SQS

##### Signals are emitted with the follwoing fields:

'id': '213667'

'created_at': '2018-05-10 11:10:08.597555',

'modified_at': '2018-05-10 11:10:08.597617',

'UI': 'telegram bot'  --- ?

'subscribers_only': 'True', ----?

'text': '',


##### every signals is emitted for a given time (timestamp), exchanger (source) and for a pair of coin like BTC/USDT (transaction_currency / counter_currency) and on data from a chart with a particular period (60/240/1440 min - resample_period)


'timestamp': '2018-05-10 11:02:00',

'source': 'binance',

'transaction_currency': 'QTUM',

'counter_currency': '0',

'resample_period': '60',

#### signal description:
signal is a name of the signal (RSI, SMA, RSI_Cumulative)

trend is what our system things about future price, trend=1 means we think price will grow, -1 we think it will drop soon

strength is a degree of our certainty about this trend, (1,2,3)

For example:
SignalType(signal='RSI', trend=-1, strength=3) means that based on RSI indicator we think that trend will be bearish with high certainty ('strength_max': '3')



'signal': 'SMA',

'trend': '1',

'risk': None,

'horizon': 'short',   ----> medium, long, in essence duplicates resample_period

'strength_value': '1',

'strength_max': '3',

#### additional information
 'price': '211000',
 'price_change': '-0.017233348858872847',
 'rsi_value': 'None',
 'volume_btc': 'None',
 'volume_btc_change': 'None',
 'volume_usdt': 'None',
 'volume_usdt_change': 'None',

#### AI probabilities of future predicted price if any
 'predicted_ahead_for': 'None',
 'probability_same': 'None',
 'probability_up': 'None',
 'probability_down': 'None',
 'sent_at': '0.0'


### possible signals in the system:
All signals can be described by three fields 'signal, trend, strength' are together might be described by the following data structure

This names are never emitted, they are internal, so you have to use 'signal, trend, strength'

SignalType = namedtuple('SignalType', 'signal, trend, strength')

ALL_SIGNALS = {

    'rsi_buy_1' : SignalType('RSI', 1, 1),
    'rsi_buy_2' : SignalType('RSI', 1, 2),
    'rsi_buy_3' : SignalType('RSI', 1, 3),
    'rsi_sell_1': SignalType(signal='RSI', trend=-1, strength=1),
    'rsi_sell_2': SignalType(signal='RSI', trend=-1, strength=2),
    'rsi_sell_3': SignalType(signal='RSI', trend=-1, strength=3),

    'rsi_cumulat_buy_2' : SignalType('RSI_Cumulative', 1, 2),
    'rsi_cumulat_buy_3' : SignalType('RSI_Cumulative', 1, 3),
    'rsi_cumulat_sell_2': SignalType('RSI_Cumulative', -1, 2),
    'rsi_cumulat_sell_3': SignalType('RSI_Cumulative', -1, 3),

    'ichi_kumo_up' : SignalType('kumo_breakout', 1, 3),
    'ichi_kumo_down' : SignalType('kumo_breakout', -1, 3),

    'sma_bull_1' : SignalType('SMA', 1, 1),  # price crosses sma50 up
    'sma_bear_1' : SignalType('SMA', -1, 1),
    'sma_bull_2' : SignalType('SMA', 1, 2),   # price crosses sma200 up
    'sma_bear_2' : SignalType('SMA', -1, 2),
    'sma_bull_3' : SignalType('SMA', 1, 3),    # sma50 crosses sma200 up
    'sma_bear_3' : SignalType('SMA', -1, 3),

    'ann_simple_bull': SignalType('ANN_Simple', 1, 3),  # price cross sma200 up
    'ann_simple_bear': SignalType('ANN_Simple', -1, 3),


}



where


