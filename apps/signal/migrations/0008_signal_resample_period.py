# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signal', '0007_auto_20171212_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='signal',
            name='resample_period',
            field=models.PositiveSmallIntegerField(default=15),
        ),
    ]