from django.db import models


class DataSchemaConstraints(models.Model):
    unique = models.BooleanField(default=False, help_text="Values in this row have to be unique")
    format = models.CharField(max_length=100, null=True, help_text="Define a format (only for Date/Time/DateTime)")
    minimum = models.CharField(null=True, max_length=100,
                               help_text="(optional) Define a minimum value (only for Number/Date/Time/DateTime) ")
    maximum = models.CharField(null=True, max_length=100, help_text="(optional) Define a maximum value")
    required = models.BooleanField(default=False, help_text="Field is required")
    min_length = models.IntegerField(null=True, verbose_name='minLength')
    max_length = models.IntegerField(null=True, verbose_name='maxLength')

    def to_dict(self):
        constraint_dict = {}
        if self.unique:
            constraint_dict['unique'] = self.unique
        if self.format:
            constraint_dict['format'] = self.format
        if self.minimum:
            constraint_dict['minimum'] = self.minimum
        if self.min_length:
            constraint_dict['min_length'] = self.min_length
        if self.max_length:
            constraint_dict['max_length'] = self.max_length
        if self.maximum:
            constraint_dict['maximum'] = self.maximum
        if self.required:
            constraint_dict['required'] = self.required
        return constraint_dict


class DataSchemaField(models.Model):
    JSON_TABLE_TYPES = (
        ('string', 'String'),
        ('integer', 'Integer'),
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
    constraints = models.ForeignKey(to=DataSchemaConstraints, null=True)

    def to_dict(self):
        obj_dict = {}
        obj_dict['name'] = self.name
        obj_dict['type'] = self.datatype
        if self.title:
            obj_dict['title'] = self.title
        if self.description:
            obj_dict['description'] = self.description
        if self.constraints:
            obj_dict['constraints'] = self.constraints.to_dict()
        return obj_dict


class DataSchema(models.Model):
    name = models.CharField(max_length=255)
    fields = models.ManyToManyField(to=DataSchemaField)

    def to_dict(self):
        schema_dict = {}
        schema_dict['fields'] = [x.to_dict() for x in self.fields.all()]
        return schema_dict

