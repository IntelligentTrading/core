# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-28 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0022_pricehistory_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='priceresampl',
            name='close_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='priceresampl',
            name='high_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='priceresampl',
            name='low_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='priceresampl',
            name='open_volume',
            field=models.FloatField(null=True),
        ),
    ]
