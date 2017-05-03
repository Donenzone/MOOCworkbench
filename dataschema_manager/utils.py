from tableschema import Schema, Table
import tableschema

from .models import DataSchemaField


def parse_json_table_schema(json_table_schema):
    schema = Schema(json_table_schema)
    data_schema_fields = []
    for field in schema.fields:
        data_field = DataSchemaField()
        data_field.name = field.name
        data_field.datatype = field.type
        data_field.required = field.required
        data_schema_fields.append(data_field)
    return data_schema_fields


def validate_schema(json_table_schema):
    try:
        tableschema.validate(json_table_schema)
        return True
    except tableschema.exceptions.SchemaValidationError as exception:
        return exception


