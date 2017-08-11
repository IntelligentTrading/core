""" Intelligent Trading Endpoints """
from google.cloud import datastore
from datetime import datetime
from flask import Flask, jsonify
from requests import get, RequestException


app = Flask(__name__)


@app.route('/poloniex', methods=['GET'])
def poloniex():
    """ Poloniex Worker """
    #todo: secure this route so only the cron can trigger it
    try:
        req = get('https://poloniex.com/public?command=returnTicker')

        client = datastore.Client()
        entity = datastore.Entity(key=client.key('Channels'),
                                  exclude_from_indexes=('content',))
        entity.update({
            'channel': 'Poloniex',
            'content': '%s' % req.json(),
            'types': 'exchange',
            'timestamp': int(datetime.now().timestamp())
        })
        client.put(entity)

        # todo: make sure indicators are subscribed to new datastore entities

    except RequestException as err:
        return jsonify({'error': err.message}), 500

    return jsonify({'added': 'Poloniex'}), 201


@app.route('/', methods=['GET'])
def index():
    """ Default route - only for check health """
    return jsonify({'status': 'Ok'}), 200


@app.errorhandler(500)
def server_error(err):
    """ Server error handle """
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
