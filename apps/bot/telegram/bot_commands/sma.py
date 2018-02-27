from apps.bot.telegram.utilities import telegram_command, TelegramBotException


@telegram_command("sma", pass_args=True)
def sma(args):
    """
    /SMA <symbol>
    returns the SMA values for any given coin symbol
    """
    assert len(args[0])

    # from utils.symbols import get_symbol

    try:
        # symbol = get_symbol(args[0])
        pass

    except TelegramBotException as e:
        print(e.developer_message)  # logger.debug(e.developer_message)
        return e.user_message

    except Exception as e:
        print(str(e))  # logger.warning(str(e))
        return "unexpected error"

    # todo: get latest sma data from datastore
    sma6, sma12, sma24 = 1, 2, 3

    # print("returning SMA for" + symbol)  # logger.debug("returning SMA for"+symbol)

    return "\n".join([
        "SMA-6: {:,}".format(sma6),
        "SMA-12: {:,}".format(sma12),
        "SMA-24: {:,}".format(sma24),
    ])

# string formatting: https://docs.python.org/3/library/string.html#format-specification-mini-language
