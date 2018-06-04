""" Commands:

info - list of supported coins, trading pairs and exchanges
"""

from telegram import ParseMode

from taskapp.helpers import get_exchanges, get_source_name
from apps.info_bot.helpers import get_currency_pairs, save_history, restore_db_connection

from settings import LOCAL



def info_view(update):

    view = f'Hello, {update.message.from_user.first_name}!\n\n'

    exchanges = (get_source_name(index).capitalize() for index in get_exchanges())
    view += f'I support these exchanges: `{", ".join(exchanges)}\n\n`'

    period_in_seconds = 2*60*60 if not LOCAL else 2000*60*60
    trading_pairs = get_currency_pairs(source='all', period_in_seconds=period_in_seconds, counter_currency_format="text")

    coins = set(coin for coin, _ in trading_pairs)

    view += f'And {len(coins)} coins:\n`{", ".join(sorted(coins))}`\n\n'

    view += f'And {len(trading_pairs)} trading pairs, like `BTC_USDT, ETH_BTC, XRP_ETH ...`'

    return view

# User Commands
@restore_db_connection
def info(bot, update):
    save_history(update)
    update.message.reply_text(info_view(update), ParseMode.MARKDOWN)
    return
