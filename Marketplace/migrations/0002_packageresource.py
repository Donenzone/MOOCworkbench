# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 13:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0001_initial'),
        ('Marketplace', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource', models.TextField()),
                ('url', models.URLField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserManager.WorkbenchUser')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Marketplace.Package')),
            ],
        ),
    ]
