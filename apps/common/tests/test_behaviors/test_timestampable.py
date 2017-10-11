from datetime import datetime
import mock
import pytz

from django.utils import timezone

from .test_mixins import BehaviorTestCaseMixin


class TimestampableTest(BehaviorTestCaseMixin):
    def test_save_model_should_save_created_at(self):
        now = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj = self.create_instance()
            self.assertEqual(obj.created_at, now)

    def test_edit_data_in_model_should_not_override_created_at(self):
        first_time = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        second_time = datetime(2016, 2, 2, tzinfo=pytz.UTC)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.side_effect = [
                first_time, first_time, second_time, second_time
            ]
            obj = self.create_instance()
            obj.save()
            self.assertEqual(obj.created_at, first_time)

    def test_edit_data_in_model_should_override_modified_at(self):
        first_time = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        second_time = datetime(2016, 2, 2, tzinfo=pytz.UTC)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.side_effect = [
                first_time, first_time, second_time, second_time
            ]
            obj = self.create_instance()
            obj.save()
            self.assertEqual(obj.modified_at, second_time)

    def test_save_model_should_save_modified_at(self):
        now = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj = self.create_instance()
            self.assertEqual(obj.modified_at, now)
