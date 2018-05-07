from telegram import ParseMode

from taskapp.helpers import get_exchanges, get_source_name
from apps.info_bot.helpers import get_currency_pairs


""" Commands:

info - list of supported coins, trading pairs and exchanges
"""

def info_view(update):
    view = f'Hello, hello, {update.message.from_user.first_name}!\n\n'

    exchanges = (get_source_name(index).capitalize() for index in get_exchanges())
    view += f'I support these exchanges: `{", ".join(exchanges)}\n\n`'

    trading_pairs = get_currency_pairs()
    coins = set(coin for coin, _ in trading_pairs)
    view += f'And {len(coins)} coins:\n`{", ".join(coins)}`\n\n'

    view += f'And {len(trading_pairs)} trading pairs, like `BTC_USDT, ETH_BTC, XRP_ETH ...` I love long text messages, but this message is already too long, even for me 🙂  '

    return view

# User Commands
def info(bot, update):
    update.message.reply_text(info_view(update), ParseMode.MARKDOWN)
    return
