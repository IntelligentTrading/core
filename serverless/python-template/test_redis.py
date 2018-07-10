import json
import redis

def test_redis(event, context):

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    r.set('test', str(event))

    body = {
        "message": "confirmed saved in cache",
        "value": r.get('test')
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
