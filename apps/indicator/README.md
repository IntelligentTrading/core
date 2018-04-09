# Indicator folder

Indicator name came from TA (Technical Analysis) terminology and means any new time series derived from raw data (which is raw price table in our case)

So, indicator folders keep all TA indicators which can be calculated for every time point. Currently they are:

### Implemented Indicators

#### Price and Volume: not indicators.
In principle they have to be moved into a separate folder like /raw_data

#### PriceResampl: agregated data
In contrast to Price which contains a price ticker every minute for different exchangers (sourse), the PriceResample re-calculated this fine-grained 1 min price timeseries into 60, 240 and 1440 timeseries of the same data
i.e. do a resampling with different periods.
Since we agregate the 60 point into one, we use the following statistics to desribe this sample:
open, close, max, min prices and variance.

#### SMA: simple indicator
At each time point (60,240,1440) is calculates SMA on aggregated close/max price from PriceResample
Several different SMAs calculated at the same time with different SMA periods: 9, 15, 30 , 60 etc

#### RSI: simple indicator
Same as SMA, but calculates RSI at each time point on PriceResample data

_Refactoring Note:_ in future it is possible to combine all simple indicators into one table/model

#### EventElementary: simple events
At each time point the simple indicators and price time series are checked for crossing, beigin one above enother etc, for example
- if sma50 crosses price up
- if sma50 crosses sma200 up
- if conversion line is above the base line (see Ichimoku)
etc

#### EventLogical: complex events carrying its own name (Kumo etc)
This is a next step after simple events checking in EventElementary.

At each time point we check for more complicated event to happen. Usually these events are carrying its widely known name like _kumo breakout up_ event

In essence the Kumo event is a logical function of a number of elementary events, for example
- if close_cloud_breakout_up AND
- lagging_above_cloud AND
- lagging_above_highest AND
- conversion_above_base
then an event is TRUE

hence the name of the table.