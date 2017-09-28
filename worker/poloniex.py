""" Intelligent Trading Poloniex Worker
"""
from requests import get, RequestException


def poloniex():
    """ Poloniex Worker """
    # todo: secure this route so only the cron can trigger it - helpful answer on stack overflow v v
    # todo: https://stackoverflow.com/questions/42767839/how-to-secure-google-cron-service-tasks-on-gap-flexible-env/42770708#42770708
    try:
        req = get('https://poloniex.com/public?command=returnTicker')

        data = req.json()

        #publish_to_indicators("Poloniex data new %d" % entity['timestamp'])

    except RequestException as err:
        return err.message, 500

    return data, 201


if __name__ == '__main__':
    print('hello')
