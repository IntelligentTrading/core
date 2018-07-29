from abc import ABC
from TA import logger, TAException


class SubscriberException(TAException):
    pass


class TASubscriber(ABC):
    classes_subscribing_to = []

    def __init__(self):
        from TA.worker import redis_client
        from TA.redis_db import database
        self.database = database
        self.pubsub = redis_client.pubsub()
        logger.info(f'New pubsub for {self.__class__.__name__}')
        for s_class in self.classes_subscribing_to:
            self.pubsub.subscribe(s_class.__class__.__name__)
            logger.info(f'{self.__class__.__name__} subscribed to '
                         f'{s_class.__class__.__name__} channel')


    def __call__(self):
        data_event = self.pubsub.get_message()
        if not data_event:
            return
        if not data_event.get('type') == 'message':
            return

        # data_event = {
        #   'type': 'message',
        #   'pattern': None,
        #   'channel': b'channel',
        #   'data': b"dude, what's up?"
        # }

        try:
            logger.debug(f'handling event in {channel} subscription')
            self.handle(data_event['channel'], data_event['data'])
        except KeyError:
            pass  # message not in expected format. just ignore
        except Exception as e:
            raise SubscriberException(str(e))


    def handle(self, channel, data, *args, **kwargs):
        """
        overwrite me with some logic
        :return: None
        """
        logger.warning(f'NEW MESSAGE for '
                       f'{self.__class__.__name__} subscribed to '
                       f'{channel} channel '
                       f'BUT HANDLER NOT DEFINED! '
                       f'... message/event discarded')
        pass
