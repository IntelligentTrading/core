from apps.bot.telegram.utilities import telegram_command


@telegram_command("help", pass_args=False)
def help_command_list():
    from apps.bot.telegram.bot_commands_index import public_commands

    return '\n'.join([
                         "Available commands:",
                     ] + [
                         "/%s - %s" % (command.execution_handle, command.help_text) for command in public_commands
                     ])


help_command_list.help_text = "list of available commands"

# "/price - list of coins with comparison \n"
# "/price USDT_BTC - last report of coin comparison \n \n"
