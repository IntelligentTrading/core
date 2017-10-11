from django.db import models
from django.utils import timezone


class Publishable(models.Model):

    published_at = models.DateTimeField(null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_published(self):
        now = timezone.now()
        if (self.published_at and self.published_at < now
                and not (self.unpublished_at and self.unpublished_at < now)):
            return True
        else:
            return False
