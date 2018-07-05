# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-28 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0023_add_volume_to_price_resampl'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='pricehistory',
            index=models.Index(fields=['timestamp', 'transaction_currency', 'counter_currency', 'source'], name='indicator_p_timesta_c7c89a_idx'),
        ),
    ]