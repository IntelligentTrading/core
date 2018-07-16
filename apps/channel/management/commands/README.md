# Channel.managment.commands

* `python manage.py poll_queue`

Read price information from SQS queue (INCOMING_SQS_QUEUE) and save it to Price, Volume (messages with subject: prices_volumes) and PriceHistory (subject: ohlc_prices) models. 

Note: we should remove fetching and saving prices to the Price, Volume in future when transition to PriceHistory will be completed.

Add `pollqueue: python manage.py poll_queue` to Procfile if you use heroku.

* `python trawl_poloniex`

Use it for debugging. It run some calculations w/o Celery.
<pre>
manage.py trawl_poloniex <arg>, where <arg>:
    * compute_indicators - compute indicators for poloniex (default)
    * compute_pair - BTC/USDT only 
    * backtest - backtest all strategies
    * ann - BE VERY VERY CAREFUL WITH THAT!!!! Because AI is our biggest existential threat.
</pre>


* `python manage.py import_from_tob_history_csv`

Read prices (open, high, low, close) from csv files with historical prices, provided by Tobias and stored in S3 bucket 'intelligenttrading-historical-dump'.

*  `python manage.py import_from_channel_exchangedata_csv`

Import historical pricess from ExchangeData model (from Core and Data App) stored in csv file.

* `python manage.py try_taliv`

Simple check if TA-Lib library installed and working.