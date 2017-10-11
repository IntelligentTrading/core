from django.db import models


class Expirable(models.Model):

    valid_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        from django.utils.timezone import now
        return True if self.expired_at and self.expired_at < now() else False

    class Meta:
        abstract = True
