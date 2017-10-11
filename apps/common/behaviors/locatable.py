from django.db import models


class Locatable(models.Model):

    address = models.ForeignKey('common.Address', null=True)

    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)

    class Meta:
        abstract = True
