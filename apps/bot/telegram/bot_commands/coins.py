import requests
from apps.bot.telegram.utilities import telegram_command
import simplejson as json
from google.cloud import datastore

@telegram_command("coins")
def coins():
    try:
        client = datastore.Client()
        query = client.query(kind='Channels', order=['-timestamp'])
        content = list(query.fetch(limit=1))[0]['content']

        result = json.loads(content.replace("'", "\""))
        msg = []

        for key in result.keys():
            msg.append(key)




        data = sorted(req.json())
        result = str(data).replace("[", "").replace("]", "").replace("'", "")

        return "\n".join([
            "Do you can choice the coin price with comparison below:",
            result,
            "for example: /price USDT_BTC",
        ])

    except Exception as e:
        return "Worker service in maintenance!"


coins.help_text = "list of all coins for using /price command"
