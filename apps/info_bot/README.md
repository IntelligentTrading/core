# ITF Info Bot

ITF Info bot is a telegram bot that shows some usefull information about cryptocurrencies and trading signals from ITF database.

Start bot with:
`python manage.py run_info_bot`

Add `infobot: python manage.py run_info_bot` to Procfile if you use heroku.

Use telegram [@BotFather](https://telegram.me/botfather) to obtain telegram bot api token, set bot name, description, list of available commands and etc.

List of commands for @BotFather:

<pre>
itf - Info about coin or trading pair. For example: `/itf BTC` or `/itf XRP_ETH`.
i - Latest info about price and volume. For example: `/i BTC`.
ta - Latest TA signals. For example: `/ta BTC`.
s - Latest crowd sentiment. For example: `/s BTC`.
price - Show price for trading pair on different exchanges. For example: `/price BTC_USDT`.
info - List of supported coins, trading pairs and exchanges.
help - List of available commands.
</pre>


## Requirements

ITF Info bot uses [python-telegram-bot package](https://github.com/python-telegram-bot/python-telegram-bot)

### Environment variables and settings

* INFO_BOT_TELEGRAM_BOT_API_TOKEN - obtain with telegram @BotFather
* INFO_BOT_CRYPTOPANIC_API_TOKEN - for cryptopanic sentiments 
* INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS - for how many seconds bot output cached
* INFO_BOT_ADMIN_USERNAME - only this admin user can use restart bot command


## Code structure

Telegram bot daemon started in:
* apps/info_bot/management/commands/run_info_bot.py, that call:
* apps/info_bot/telegram/start_info_bot.py (it registers telegram commands as handlers and starts daemon)

* apps/info_bot/helpers.py - common code helpers for all commands
* apps/info_bot/telegram/bot_commands/ - folder with code of bot commands

ITF Info bot saves usage log to the InfoBotHistory model:
* apps/info_bot/models/info_bot_history.py
