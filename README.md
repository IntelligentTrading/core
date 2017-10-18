# ITT Data-Sources


## API

### Price

Get the current trading price for any token

GET `/price`
PARAMS `coin = <token ticker>`

eg. `/price?=coin=BTC`

JSON RESPONSE

`{'price': <int, satoshis>, 'timestamp': timestamp}`

eg.
`{"price": 281000, "timestamp": "2017-10-18 04:18:51.269170"}`

token ticker is <8 chars should be all caps



### Volume

Get the current trading volume for any token

GET `/volume`
PARAMS `coin = <token ticker>`

eg. `/volume?=coin=BTC`

token ticker is <8 chars should be all caps

JSON RESPONSE

`{'volume': <float, BTC>, 'timestamp': timestamp}`

eg.
`{"volume": 63.3236288, "timestamp": "2017-10-18 03:41:17.902490"}`

