import logging
import unittest

from django.test import SimpleTestCase

from taskapp.helpers import get_source_name



class TestHelpers(SimpleTestCase):

    def test_get_source_name(self):
        self.assertEqual(get_source_name(0), 'poloniex')
        self.assertEqual(get_source_name(2), 'binance')


 