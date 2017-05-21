# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-19 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build_manager', '0014_auto_20170519_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travisinstance',
            name='last_build_status',
            field=models.CharField(choices=[('C', 'Cancelled'), ('S', 'Success'), ('F', 'Failed')], max_length=1, null=True),
        ),
    ]