from .test_mixins import BehaviorTestCaseMixin
from ...models import Address


class LocatableTest(BehaviorTestCaseMixin):
    def test_should_save_address_logtitude_latitude_correctly(self):
        address = Address.objects.create()
        obj = self.create_instance(
            address=address,
            latitude="10",
            longitude="20"
        )
        self.assertEqual(obj.address, address)
        self.assertEqual(obj.latitude, "10")
        self.assertEqual(obj.longitude, "20")
