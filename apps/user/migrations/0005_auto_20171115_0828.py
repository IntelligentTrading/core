# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-15 08:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20171115_0824'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='beta_subscription_token',
            new_name='_beta_subscription_token',
        ),
    ]
