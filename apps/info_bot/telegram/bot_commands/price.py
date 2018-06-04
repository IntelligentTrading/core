""" 
Commands:
/price - Show price for the trading pair at the different exchanges. For example: /price BTC_USDT
"""
from telegram import ParseMode

from settings import COUNTER_CURRENCIES

from apps.indicator.models import Price

from apps.info_bot.helpers import (format_currency, format_timestamp, restore_db_connection,
                                   get_currency_pairs, natural_join, parse_trading_pair_string,
                                   parse_telegram_cryptocurrency_args, trading_pairs_for, save_history)

from taskapp.helpers import get_source_name, get_exchanges



def price_view(trading_pair):
    view = ''

    currency_symbol = trading_pair['counter_currency']

    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    exchanges = get_exchanges()

    last_prices_object = Price.objects.filter(
        source__in=exchanges,
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp')[:len(exchanges)]


    seen = set()
    seen_add = seen.add
    # remove dublicates
    unique_last_prices = [price for price in last_prices_object if not (price.source in seen or seen_add(price.source))]

    #exchanges_with_price = natural_join([get_source_name(price.source).title() for price in unique_last_prices])
    #view += f"I found *{currency}*\_{trading_pair['counter_currency']} in {exchanges_with_price}\n"

    for price_obj in sorted(unique_last_prices, key=lambda pr: pr.price):
        view += f"\n{format_currency(price_obj.price, currency_symbol)} on {get_source_name(price_obj.source).title()} at {format_timestamp(price_obj.timestamp)}"

    return view

## user commands
@restore_db_connection
def price(bot, update, args):
    save_history(update)
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='price')
    if trading_pair:
        view = price_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return
