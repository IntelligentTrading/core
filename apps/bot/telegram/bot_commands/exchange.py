from apps.bot.telegram.utilities import telegram_command


@telegram_command("exchanges")
def exchanges():

    return '\n'.join([
        "Options: ",
        "Poloniex",
        "Bittrex",
        "Binance",
        "",
        "set with command",
        "/exchange <name>"
    ])


exchanges.help_text = "list of supported exchanges"


@telegram_command("exchange", pass_args=True)
def exchange(args):

    if 'POLO' in args[0].upper():
        return "Poloniex exchange set as default"
    else:
        return "Only Poloniex is available. Poloniex exchange set as default."

exchange.help_text = "set the default exchange"
