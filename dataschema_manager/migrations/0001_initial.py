# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 11:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSchema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DataSchemaConstraints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique', models.BooleanField(default=False, verbose_name='Values in this row have to be unique')),
                ('format', models.CharField(blank=True, max_length=100, verbose_name='Define a format (only for Date/Time/DateTime)')),
                ('minimum', models.CharField(blank=True, max_length=100, verbose_name='(optional) Define a minimum value (only for Number/Date/Time/DateTime) ')),
                ('maximum', models.CharField(blank=True, max_length=100, verbose_name='(optional) Define a maximum value')),
                ('required', models.BooleanField(default=False, verbose_name='Field is required')),
                ('min_length', models.IntegerField(null=True)),
                ('max_length', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataSchemaField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name of row')),
                ('datatype', models.CharField(choices=[('string', 'String'), ('number', 'Number'), ('date', 'Date'), ('time', 'Time'), ('datetime', 'DateTime'), ('year', 'Year'), ('yearmonth', 'Year Month'), ('boolean', 'Boolean'), ('object', 'Object'), ('geopoint', 'GeoPoint'), ('array', 'Array'), ('duration', 'Duration'), ('any', 'Any')], max_length=100)),
                ('primary_key', models.BooleanField(default=False, verbose_name='Field is a primary key')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='Title of field')),
                ('description', models.TextField(blank=True, verbose_name='Description of the contents of the field')),
                ('constraints', models.ManyToManyField(to='dataschema_manager.DataSchemaConstraints')),
            ],
        ),
        migrations.AddField(
            model_name='dataschema',
            name='fields',
            field=models.ManyToManyField(to='dataschema_manager.DataSchemaField'),
        ),
    ]
