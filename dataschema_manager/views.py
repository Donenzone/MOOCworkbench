from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from django.db import transaction
from django.forms import inlineformset_factory
from django.forms import formset_factory

from experiments_manager.helper import verify_and_get_experiment

from .models import DataSchemaField, DataSchemaConstraints, DataSchema
from .forms import DataSchemaFieldForm, DataSchemaConstraintForm
from .mixins import DataSchemaFieldListMixin


class DataSchemaFieldCreateView(DataSchemaFieldListMixin, CreateView):
    model = DataSchemaField
    form_class = DataSchemaFieldForm
    template_name = 'dataschema_manager/dataschemafield_overview.html'

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


def dataschema_edit(request, pk):
    dataschema = DataSchemaField.objects.get(pk=pk)
    constraints = dataschema.constraints
    if request.POST:
        edit_form = DataSchemaFieldForm(request.POST, instance=dataschema)
        constraint_form = DataSchemaConstraintForm(request.POST, instance=constraints)
        if edit_form.is_valid() and constraint_form.is_valid():
            constraints.save()
            dataschema.constraint = constraints
            dataschema.save()
        else:
            return render(request, 'dataschema_manager/dataschemafield_edit.html',
                          {'form': edit_form, 'constraint_form': constraint_form})
    else:
        edit_form = DataSchemaFieldForm(instance=dataschema)
        constraint_form = DataSchemaConstraintForm(instance=constraints)
        return render(request, 'dataschema_manager/dataschemafield_edit.html', {'form': edit_form, 'constraint_form': constraint_form})