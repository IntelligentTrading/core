"""
Send ITF sns signals to http API endpoint.

Add API_KEY environment varible with access key.
Add SNS queue with signals (itf-sns-core-signals-production) as aws trigger.
"""

from __future__ import print_function
import json
import os
import urllib.parse
import urllib.request



HTTP_TIMEOUT_IN_SECONDS = 10

# enable for very fast request
# HTTP_TIMEOUT_IN_SECONDS = 0.01

DEBUG = False

if DEBUG:
    # API_KEY = 'some secret key'
    # API_URL = 'http://ptsv2.com/t/6hrb7-1544984414/post'
    API_KEY = os.environ['API_KEY']
    API_URL = 'https://zignaly.com/api/signals.php'
else:
    API_KEY = os.environ['API_KEY']
    API_URL = 'https://zignaly.com/api/signals.php'


def lambda_handler(event, context):
    if DEBUG:
        print(f"Event:\n{event}")

    message = json.loads(event['Records'][0]['Sns']['Message'])

    if good_signal(message):
        zignal = create_zignal_from(message)

        data = urllib.parse.urlencode(zignal).encode('ascii') # data should be bytes
        req = urllib.request.Request(API_URL, data)
        try:
            print(f"Sending signal:{zignal}\nto:{API_URL}")
            resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_IN_SECONDS)
            print(f"Response: {resp.code}")
        except:
            pass
    return None

def create_zignal_from(m):
    pair = f"{m['transaction_currency']}{get_counter_currency(m['counter_currency'])}"
    zignal = {
        'pair': pair,
        'key': API_KEY,
        'type': buy_or_sell(m),
        'exchange': m['source'].capitalize(),
        'MDSIGNAL': m['signal'],
    }
    if DEBUG:
        print(f"Zignal: {zignal}") 
    return zignal

def good_signal(m):
    if  m['source'] == 'binance' and \
        m['signal'] in ('VBI', 'RSI', 'kumo_breakout', 'RSI_Cumulative') and \
        m['resample_period'] in ('60',) and \
        m['trend'] in ('1',): # send only buy signals, m['trend'] in ('1', '-1') - send all \
            return True
    else:
        return False

def buy_or_sell(m):
    return 'buy' if m['trend'] == '1' else 'sell'

def get_counter_currency(counter_currency_index):
    counter_currencies = ('BTC', 'ETH', 'USDT', 'XMR')
    return counter_currencies[int(counter_currency_index)]
