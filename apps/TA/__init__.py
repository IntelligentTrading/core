import os
import logging

from settings import SHORT, MEDIUM, LONG
# PERIODS_1HR, PERIODS_4HR, PERIODS_24HR = SHORT/5, MEDIUM/5, LONG/5

JAN_1_2017_TIMESTAMP = 1483228800
PERIODS_1HR, PERIODS_4HR, PERIODS_24HR = 12, 48, 288


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
