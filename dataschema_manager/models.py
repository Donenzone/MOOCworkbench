from django.db import models


class DataSchemaConstraints(models.Model):
    unique = models.BooleanField(default=False, help_text="Values in this row have to be unique")
    format = models.CharField(max_length=100, blank=True, help_text="Define a format (only for Date/Time/DateTime)")
    minimum = models.CharField(blank=True, max_length=100,
                               help_text="(optional) Define a minimum value (only for Number/Date/Time/DateTime) ")
    maximum = models.CharField(blank=True, max_length=100, help_text="(optional) Define a maximum value")
    required = models.BooleanField(default=False, help_text="Field is required")
    min_length = models.IntegerField(null=True, verbose_name='minLength')
    max_length = models.IntegerField(null=True, verbose_name='maxLength')


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

    name = models.CharField(max_length=100, help_text="Name of row")
    datatype = models.CharField(max_length=100, choices=JSON_TABLE_TYPES, verbose_name='type')
    primary_key = models.BooleanField(default=False, help_text="Field is a primary key")
    title = models.CharField(max_length=100, blank=True, help_text="Title of field")
    description = models.TextField(blank=True, help_text="Description of the contents of the field")
    constraints = models.ManyToManyField(to=DataSchemaConstraints)

    def to_dict(self):
        model_dict = {}
        for field_name in self._meta.get_all_field_names():
            print(field_name)
            field_instance = self._meta.get_field(field_name)
            field_attr = getattr(self, field_name)
            if field_instance.verbose_name:
                model_dict[field_instance.verbose_name] = field_attr
            else:
                model_dict[field_name] = field_attr
        print(model_dict)
        return model_dict


class DataSchema(models.Model):
    name = models.CharField(max_length=255)
    fields = models.ManyToManyField(to=DataSchemaField)

