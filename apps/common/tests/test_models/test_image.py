from django.test import TestCase

from ..test_behaviors import UploadableTest
from ...models import Image


class ImageTest(UploadableTest, TestCase):
    model = Image
