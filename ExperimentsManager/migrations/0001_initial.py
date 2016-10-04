# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-04 12:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WorkerManager', '0001_initial'),
        ('UserManager', '0001_initial'),
        ('GitManager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(max_length=200)),
                ('added', models.DateField(auto_now_add=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('git_repo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GitManager.GitRepository')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserManager.WorkbenchUser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExperimentRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CR', 'Created'), ('RU', 'Running'), ('SU', 'Success'), ('ER', 'Error'), ('CA', 'Cancelled')], default='CR', max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('output', models.TextField(blank=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ExperimentsManager.Experiment')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserManager.WorkbenchUser')),
                ('selected_worker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='WorkerManager.Worker')),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(max_length=200)),
                ('added', models.DateField(auto_now_add=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserManager.WorkbenchUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
