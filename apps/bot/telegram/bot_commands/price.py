import time
from google.cloud import datastore
from apps.bot.telegram.utilities import telegram_command
from apps.indicator.models import Price


@telegram_command("price", pass_args=True)
def price(args):
    try:
        coin_ticker = args[0].upper()

        price_object = Price.objects.filter(transaction_currency=coin_ticker).order_by("-timestamp").first()

        return "\n".join([
            coin_ticker + " Price",
            price_object.price_humanized,
            "as of %ds ago" % int(time.time() - datastore['timestamp'])
        ])

    except Exception as e:
        print(str(e))
        return "Please check the name of coin. Coin not found!"

price.help_text = "get the BTC price for any coin eg. /price ETH"
