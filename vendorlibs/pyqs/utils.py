import base64
import json
import pickle


def decode_message(message):
    message_body = message.get_body()
    return json.loads(message_body)

# Don't pretend to support celery msgs
# def decode_celery_message(json_task):
#     message = base64.decodestring(json_task['body'])
#     try:
#         return json.loads(message)
#     except ValueError:
#         pass
#     return pickle.loads(message)


def function_to_import_path(function):
    return "{}.{}".format(function.__module__, function.__name__)
