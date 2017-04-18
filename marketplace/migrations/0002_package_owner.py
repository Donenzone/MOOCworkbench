# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-18 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='user_manager.WorkbenchUser'),
            preserve_default=False,
        ),
    ]
