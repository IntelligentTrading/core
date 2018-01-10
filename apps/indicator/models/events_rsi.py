from apps.indicator.models.abstract_indicator import AbstractIndicator

import logging
import numpy as np

logger = logging.getLogger(__name__)


class EventsRsi(AbstractIndicator):
    def _rsi_brackets(self):
        pass

    def check_event(self):
        pass
