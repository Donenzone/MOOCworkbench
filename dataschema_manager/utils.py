import json

import tableschema
from tableschema import Schema, Table

from git_manager.helpers.github_helper import GitHubHelper

from .models import DataSchema, DataSchemaField

SCHEMA_FILE_LOCATION = 'schema/schema.json'


def get_schema_file(experiment):
    github_helper = GitHubHelper(experiment.owner, experiment.git_repo.name)
    schema = github_helper.view_file(SCHEMA_FILE_LOCATION)
    json_schema = json.loads(schema)
    result = parse_json_table_schema(json_schema)
    data_schema = experiment.schema
    data_schema.fields.add(*result)
    data_schema.save()


def parse_json_table_schema(json_table_schema):
    schema = Schema(json_table_schema)
    data_schema_fields = []
    for field in schema.fields:
        data_field = DataSchemaField()
        data_field.name = field.name
        data_field.datatype = field.type
        data_field.required = field.required
        data_field.save()
        data_schema_fields.append(data_field)
    return data_schema_fields


def validate_schema(json_table_schema):
    try:
        tableschema.validate(json_table_schema)
        return True
    except tableschema.exceptions.SchemaValidationError as exception:
        return exception
