import logging
import unittest

from django.test import SimpleTestCase

from taskapp.helpers import get_source_name, get_source_code



class TestHelpers(SimpleTestCase):

    def test_get_source_name(self):
        self.assertEqual(get_source_name(0), 'poloniex')
        self.assertEqual(get_source_name(2), 'binance')
 
    def test_get_source_code(self):
        self.assertEqual(get_source_code('poloniex'), 0)
        self.assertEqual(get_source_code('binance'), 2)
 