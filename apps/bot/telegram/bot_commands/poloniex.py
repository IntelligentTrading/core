import simplejson as json
from google.cloud import datastore
from apps.bot.telegram.utilities import telegram_command


@telegram_command("poloniex", pass_args=True)
def poloniex(args):
    try:
        client = datastore.Client()
        query = client.query(kind='Channels', order=['-timestamp'])
        content = list(query.fetch(limit=1))[0]['content']
        price_data = json.loads(content.replace("'", "\""))

        new_args = str(args).replace("[", "").replace("]", "").replace("'", "")
        data = price_data[new_args]

        return "\n".join([
            "Base Volume: %s" % data['baseVolume'],
            "High Last 24hr: %s" % data['high24hr'],
            "Highest Bid: %s" % data['highestBid'],
            "Last Price: %s" % data['last'],
            "Low Last 24hr: %s" % data['low24hr'],
            "Lowest Ask: %s" % data['lowestAsk'],
            "Percent Change: %s" % data['percentChange'],
            "Quote Volume: %s" % data['quoteVolume'],
        ])

    except Exception as e:
        print(str(e))
        return "Please check the name of coin. Coin not found!"

poloniex.help_text = "get the price for any coin pair in /coins"
