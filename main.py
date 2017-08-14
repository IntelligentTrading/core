""" Intelligent Trading Endpoints """
from google.cloud import datastore
from google.cloud import pubsub
from datetime import datetime
import os
from flask import Flask, jsonify, current_app, request
from requests import get, RequestException


app = Flask(__name__)

try:
    app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']
except:
    pass
app.config['PUBSUB_TOPIC'] = "indicators-topic"


def publish_to_indicators(message):
    """
    Publish to GCP Pub/Sub for Indicators to subscribe and update
    :param message: string
    :return: None
    """
    print("publishing message: \"" + message + "\" to pubsub topic")
    ps = pubsub.Client()
    topic = ps.topic(current_app.config['PUBSUB_TOPIC'])
    topic.publish(message.encode())


@app.route('/poloniex', methods=['GET'])
def poloniex():
    """ Poloniex Worker """
    # todo: secure this route so only the cron can trigger it - helpful answer on stack overflow v v
    # todo: https://stackoverflow.com/questions/42767839/how-to-secure-google-cron-service-tasks-on-gap-flexible-env/42770708#42770708
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

        publish_to_indicators("Poloniex data new %d" % entity['timestamp'])

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
