from datetime import datetime
import mock
import pytz

from .test_mixins import BehaviorTestCaseMixin


class PublishableTest(BehaviorTestCaseMixin):
    def test_should_store_time_correctly(self):
        published_at = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        unpublished_at = datetime(2015, 1, 2, tzinfo=pytz.UTC)

        obj = self.create_instance(
            published_at=published_at,
            unpublished_at=unpublished_at
        )

        self.assertEqual(obj.published_at, published_at)
        self.assertEqual(obj.unpublished_at, unpublished_at)
        self.assertEqual(obj.unpublished_at, unpublished_at)

    @mock.patch("apps.common.behaviors.publishable.timezone.now")
    def test_return_true_for_is_published(self, mock_now):
        mock_now.return_value = datetime(2015, 1, 15, tzinfo=pytz.UTC)
        published_at = datetime(2015, 1, 10, tzinfo=pytz.UTC)
        unpublished_at = datetime(2015, 1, 17, tzinfo=pytz.UTC)

        obj = self.create_instance(
            published_at=published_at,
            unpublished_at=unpublished_at
        )

        self.assertTrue(obj.is_published)

    @mock.patch("apps.common.behaviors.publishable.timezone.now")
    def test_return_false_for_is_published_when_published_more_than_now(
        self, mock_now
    ):
        mock_now.return_value = datetime(2015, 1, 15, tzinfo=pytz.UTC)
        published_at = datetime(2015, 1, 16, tzinfo=pytz.UTC)
        unpublished_at = datetime(2015, 1, 17, tzinfo=pytz.UTC)

        obj = self.create_instance(
            published_at=published_at,
            unpublished_at=unpublished_at
        )

        self.assertFalse(obj.is_published)

    @mock.patch("apps.common.behaviors.publishable.timezone.now")
    def test_return_false_for_is_published_when_unpublished_at_less_than_now(
        self, mock_now
    ):
        mock_now.return_value = datetime(2015, 1, 15, tzinfo=pytz.UTC)
        published_at = datetime(2015, 1, 12, tzinfo=pytz.UTC)
        unpublished_at = datetime(2015, 1, 13, tzinfo=pytz.UTC)

        obj = self.create_instance(
            published_at=published_at,
            unpublished_at=unpublished_at
        )

        self.assertFalse(obj.is_published)
