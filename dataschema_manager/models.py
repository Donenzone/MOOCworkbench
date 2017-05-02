from django.db import models


class DataSchemaField(models.Model):
    JSON_TABLE_TYPES = (
        ('string', 'String'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'DateTime'),
        ('year', 'Year'),
        ('yearmonth', 'Year Month'),
        ('boolean', 'Boolean'),
        ('object', 'Object'),
        ('geopoint', 'GeoPoint'),
        ('array', 'Array'),
        ('duration', 'Duration'),
        ('any', 'Any'),
    )

    name = models.CharField(max_length=100, verbose_name="Name of row")
    datatype = models.CharField(max_length=100, choices=JSON_TABLE_TYPES)
    primary_key = models.BooleanField(default=False, verbose_name="Field is a primary key")
    required = models.BooleanField(default=False, verbose_name="Field is required")
    title = models.CharField(max_length=100, blank=True, verbose_name="Title of field")
    description = models.TextField(blank=True, verbose_name="Description of the contents of the field")
    unique = models.BooleanField(default=False, verbose_name="Values in this row have to be unique")
    format = models.CharField(max_length=100, blank=True, verbose_name="Define a format (only for Date/Time/DateTime)")
    minimum = models.CharField(blank=True, max_length=100, verbose_name="(optional) Define a minimum value (only for Number/Date/Time/DateTime) ")
    maximum = models.CharField(blank=True, max_length=100, verbose_name="(optional) Define a maximum value")
