import requests
import json

eth_addresses = [
    "0xb12b399cA36e9F89791cA91ABEf8eAc74fc05c52",  # 50
    "0x8338bCD380b4380191F71de310e338223Af02357",  # 20
    "0xfcF9fA13978D6B6825A3c75342dF28DcF86559a1",  # 10
    "0x57677cea00492982AEf8da2F75635E69ec64f872",  # 0
]

btc_addresses = [
    "12Cyt8eJ2mWah12esHGSSTFuWXFfcCuqB5",  # 50
    "1Mptoc1pQRpB4E2cPpxGrG9tAiehh7gEue",  # 20
    "1ACydwVvcW5XERpLBy4AHvwTLgzicN1k2F",  # 10
    "1F6fhLSVnnv9NZ8v6Sevsve5PLUcezXpQy",  # 0
]


def getTotalBalances():
    eth_total = sum([getETHBalance(address) for address in eth_addresses])
    btc_total = sum([getBTCBalance(address) for address in btc_addresses])
    usd_total = int((eth_total * 300) + (btc_total * 4300))

    print(eth_total, btc_total, usd_total)
    return (eth_total, btc_total, usd_total)


def getETHBalance(eth_address):
    #  alt_url = 'https://api.etherscan.io/api?module=account&action=balance&address=' + ethAddress + '&tag=latest&apikey=YourApiKeyToken'
    r = requests.get('https://api.ethplorer.io/getAddressInfo/' + eth_address + '?apiKey=freekey')
    data = json.loads(r.text)
    try:
        return float(data["ETH"]['balance'])
    except:
        return 0


def getBTCBalance(btc_address):
    r = requests.get('https://blockexplorer.com/api/addr/' + btc_address + '/balance')
    try:
        return float(r.text) / 100000000
    except:
        return 0


from apps.bot.telegram.utilities import telegram_command


@telegram_command("tokensale", pass_args=False)
def tokensale():
    (eth, btc, usd) = getTotalBalances()

    return '\n'.join([
        "%d ETH" % eth,
        "%d BTC" % btc,
        "%d USD" % usd,
        "%2.1f%%  of $4.2M cap" % (usd/42000),
        "",
        "btw, please don't ask me again every 5 min or I might get my API access revoked and stop working. k, thx, bye :)",
    ])

tokensale.help_text = "get funding update on token sale"
