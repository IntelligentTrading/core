from apps.bot.telegram.utilities import telegram_command


@telegram_command("start", pass_args=False)
def start():
    return "\n".join([
        "Welcome to Intelligent Trading Bot!",
        "You are now subscribed to price alerts.",
        "try /help for a list of commands and examples",
    ])


start.help_text = "subscribe to new alerts"
