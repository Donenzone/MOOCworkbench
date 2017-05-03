from django.shortcuts import render
from django.views.generic import CreateView
from django.db import transaction

from experiments_manager.helper import verify_and_get_experiment

from .models import DataSchemaField, DataSchemaConstraints, DataSchema
from .forms import DataSchemaFieldForm
from .mixins import DataSchemaFieldListMixin


class DataSchemaFieldCreateView(DataSchemaFieldListMixin, CreateView):
    model = DataSchemaField
    form_class = DataSchemaFieldForm

    def form_valid(self, form):
        experiment = verify_and_get_experiment(self.request, self.kwargs['experiment_id'])
        data_schema_constraint = self.create_data_schema_constraints(form)
        data_schema = self.get_data_schema(experiment)
        with transaction.atomic():
            form.instance.constraints = data_schema_constraint
            response = super(DataSchemaFieldCreateView, self).form_valid(form)
            data_schema.fields.add(form.instance)
            data_schema.save()
        return response

    def create_data_schema_constraints(self, form):
        data_schema_constraints = DataSchemaConstraints()
        data_schema_constraints.unique = form.cleaned_data['unique']
        data_schema_constraints.format = form.cleaned_data['format']
        data_schema_constraints.required = form.cleaned_data['required']
        if form.cleaned_data['min_length']:
            data_schema_constraints.min_length = int(form.cleaned_data['min_length'])
        if form.cleaned_data['max_length']:
            data_schema_constraints.max_length = int(form.cleaned_data['max_length'])
        if form.cleaned_data['maximum']:
            data_schema_constraints.minimum = str(form.cleaned_data['minimum'])
        if form.cleaned_data['maximum']:
            data_schema_constraints.maximum = str(form.cleaned_data['maximum'])
        data_schema_constraints.save()
        return data_schema_constraints

    def get_data_schema(self, experiment):
        data_schema = DataSchema.objects.filter(name='main')
        if not data_schema:
            data_schema = DataSchema.objects.create(name='main')
            experiment.schema.add(data_schema)
            experiment.save()
            return data_schema
        return data_schema[0]

