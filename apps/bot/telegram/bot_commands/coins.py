import requests
from apps.bot.telegram.utilities import telegram_command
import simplejson as json
from google.cloud import datastore

@telegram_command("coins")
def coins():
    try:

        from settings import BTC_COINS, USDT_COINS
        coins_list = set(BTC_COINS + USDT_COINS)

        coin_list_string = " ".join(coins_list)

        return "\n".join([
            "Coins currently being tracked:",
            coin_list_string,
        ])

    except Exception as e:
        return "Problem with coins command: " + str(e)

coins.help_text = "list of all coins for using /price command"
