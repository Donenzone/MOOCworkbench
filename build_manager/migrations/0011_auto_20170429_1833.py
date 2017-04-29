# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-29 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build_manager', '0010_auto_20170428_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travisinstance',
            name='last_build_status',
            field=models.CharField(choices=[('C', 'Cancelled'), ('F', 'Failed'), ('S', 'Success')], max_length=1, null=True),
        ),
    ]
