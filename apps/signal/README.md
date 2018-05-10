# Signal folder
For now only contains a Signal model which is in essence a log of all emitted signals to SQS

Signals are emitted with the follwoing fields:

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

 'signal': 'SMA',
 'trend': '1',
 'risk': None,
 'horizon': 'short',
 'strength_value': '1',
 'strength_max': '3',
 'price': '211000',
 'price_change': '-0.017233348858872847',
 'rsi_value': 'None',
 'volume_btc': 'None',
 'volume_btc_change': 'None',
 'volume_usdt': 'None',
 'volume_usdt_change': 'None',
 'predicted_ahead_for': 'None',
 'probability_same': 'None',
 'probability_up': 'None',
 'probability_down': 'None',
 'sent_at': '0.0'}


### possible signals in the system:


