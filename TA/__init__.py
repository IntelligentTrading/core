import os
import logging

deployment_type = os.environ.get('DEPLOYMENT_TYPE', 'LOCAL')
if deployment_type == 'LOCAL':
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('flask_app')


class TAException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)

class SuchWowException(Exception):
    def __init__(self, message):
        self.message = message
        such_wow = "==============SUCH=====WOW==============="
        logger.error(f'\n\n{such_wow}\n\n{message}\n\n{such_wow}')
