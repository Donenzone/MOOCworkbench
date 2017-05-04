from django.shortcuts import render, redirect
from django.views.generic import View
from django.db import transaction
from django.contrib.auth.decorators import login_required

from experiments_manager.helper import verify_and_get_experiment

from .models import DataSchemaField
from .forms import DataSchemaFieldForm, DataSchemaConstraintForm
from .utils import get_data_schema


@login_required
def dataschema_overview(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    context = {}
    data_schema = experiment.schema.first()
    context['data_schema_list'] = data_schema.fields.all()
    context['experiment_id'] = experiment.id
    context['form'] = DataSchemaFieldForm()
    context['constraint_form'] = DataSchemaConstraintForm()
    return render(request, 'dataschema_manager/dataschemafield_overview.html', context)


@login_required
def dataschema_new(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    context = {}
    if request.POST:
        edit_form = DataSchemaFieldForm(request.POST)
        constraint_form = DataSchemaConstraintForm(request.POST)
        if edit_form.is_valid() and constraint_form.is_valid():
            with transaction.atomic():
                constraint_form.save()
                edit_form.instance.constraints = constraint_form.instance
                edit_form.save()
                data_schema = get_data_schema(experiment)
                data_schema.fields.add(edit_form.instance)
                data_schema.save()
            return redirect(to=experiment.get_absolute_url('schema'))
        else:
            context['form'] = edit_form
            context['constraint_form'] = constraint_form
            return render(request, 'dataschema_manager/dataschemafield_edit.html', context)


@login_required
def dataschema_edit(request, pk, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    dataschema = DataSchemaField.objects.get(pk=pk)
    constraints = dataschema.constraints
    context = {}
    context['schema_id'] = dataschema.pk
    context['experiment_id'] = experiment.id
    if request.POST:
        edit_form = DataSchemaFieldForm(request.POST, instance=dataschema)
        constraint_form = DataSchemaConstraintForm(request.POST, instance=constraints)
        if edit_form.is_valid() and constraint_form.is_valid():
            constraints.save()
            dataschema.constraint = constraints
            dataschema.save()
            return redirect(to=experiment.get_absolute_url('schema'))
        else:
            context['form'] = edit_form
            context['constraint_form'] = constraint_form
            return render(request, 'dataschema_manager/dataschemafield_edit.html', context)
    else:
        context['form'] = DataSchemaFieldForm(instance=dataschema)
        context['constraint_form'] = DataSchemaConstraintForm(instance=constraints)
        return render(request, 'dataschema_manager/dataschemafield_edit.html', context)


@login_required
def dataschema_to_github(request, pk, experiment_id):
    pass
