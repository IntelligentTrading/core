# Indicator.management.commands

* `python manage.py fill_price_history_missing_volumes`

This command fills missing volumes in PriceHistory with data from Volume model.
It starts with recent items from PriceHistory.
You should use a parameter with a number of PriceHistory entries it should fill.
This command uses DataFiller class from indicator.management.helpers.


* `python manage.py fill_price_resampl_volume_history`

This command fills missing volumes in PriceResampl with data from PriceHistory.
It takes a parameter with a number of entries it should fill.
