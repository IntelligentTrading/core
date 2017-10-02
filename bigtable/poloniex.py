""" Intelligent Trading Poloniex Worker
"""
from requests import get, RequestException
from input_data import input_data
import time
import json


def poloniex():
    """ Poloniex Worker """
    # todo: secure this route so only the cron can trigger it - helpful answer on stack overflow v v
    # todo: https://stackoverflow.com/questions/42767839/how-to-secure-google-cron-service-tasks-on-gap-flexible-env/42770708#42770708
    try:
        req = get('https://poloniex.com/public?command=returnTicker')
        data = req.json()
        timestamp = int(time.time())
        row_key = 'poloniex#%s' % timestamp

        aux_dict = {}

        for parser in sorted(data):
            #col_family = parser.split('_')[0]

            aux_dict["{}_LAST".format(parser)] = "{}".format(data[parser]['last'])
            aux_dict["{}_CHANGE".format(parser)] = "{}".format(data[parser]['percentChange'])
            aux_dict["{}_HIGH".format(parser)] = "{}".format(data[parser]['high24hr'])
            aux_dict["{}_LOW".format(parser)] = "{}".format(data[parser]['low24hr'])
            aux_dict["{}_VOLUME".format(parser)] = "{}".format(data[parser]['baseVolume'])

            print(aux_dict)
            exit()

            #input_json.update({"data": {col_family} })
            #col = '{}{}'.format(parser, '_LAST')
            """
            new_data = input_data(project_id='optimal-oasis-170206',
                            instance_id='itt-develop',
                            table_id='channels',
                            data=input_json)
            """
        #print(input_json)
        #print(json.dumps(input_json, sort_keys=True, indent=4))
        
    except RequestException as error:
        return error.message, 500

    return "OKay", 201


if __name__ == '__main__':
    poloniex()
