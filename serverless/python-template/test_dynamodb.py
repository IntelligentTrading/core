import os
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
indicators_table = dynamodb.Table(os.environ['DYNAMODB_INDICATORS_TABLE'])

def test_dynamodb(event, context):

    try:
        db_response = indicators_table.get_item(
            Key={'primary_key': "special-string-key"}
        )
        message = "it was already there"
    except:
        db_response = indicators_table.put_item(
            Item = {
                'primary_key': "special-string-key",
                'unix_timestamp': 1527760162,
                'created_at': str(int(time.mktime((datetime.now()).timetuple()))),
                'modified_at': str(int(time.mktime((datetime.now()).timetuple()))),
            }
        )
        message = "pretty sure we saved in the db"

    body = {"message": message,
            "db_response": json.dumps(db_response)
            }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
