# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 09:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitRepository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=200)),
                ('has_issues', models.BooleanField(default=True)),
                ('has_wiki', models.BooleanField(default=True)),
                ('github_url', models.URLField()),
                ('private', models.BooleanField(default=False)),
                ('hooks_url', models.CharField(max_length=100, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_manager.WorkbenchUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
