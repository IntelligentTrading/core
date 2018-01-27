from apps.bot.telegram.utilities import telegram_command, ChatBotException


@telegram_command("ema", pass_args=True)
def ema(args):
    """
    /EMA <symbol>
    returns the EMA values for any given coin symbol
    """
    assert len(args[0])

    # from utils.symbols import get_symbol
    # from indicators.price import get_current_price_humanized

    try:
        # symbol = get_symbol(args[0])
        pass

    except ChatBotException as e:
        # logger.debug(e.developer_message)
        return e.user_message

    except Exception as e:
        # logger.warning(str(e))
        return "unexpected error"

    # todo: get latest ema data from datastore
    ema6, ema12, ema24 = 1, 2, 3

    # print("returning EMA for" + symbol)  # logger.debug("returning EMA for"+symbol)

    return "\n".join([
        # symbol + " " + get_current_price_humanized(symbol) + " EMA analysis",
        "EMA-6: {:,}".format(ema6),
        "EMA-12: {:,}".format(ema12),
        "EMA-24: {:,}".format(ema24),
    ])
