# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('git_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha_hash', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField()),
                ('commit_message', models.CharField(max_length=1000)),
                ('username', models.CharField(max_length=255)),
                ('additions', models.IntegerField(null=True)),
                ('deletions', models.IntegerField(null=True)),
                ('total', models.IntegerField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='gitrepository',
            name='commits',
            field=models.ManyToManyField(to='git_manager.Commit'),
        ),
    ]
