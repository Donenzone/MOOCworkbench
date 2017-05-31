import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from experiments_manager.consumers import send_message
from experiments_manager.helper import MessageStatus, verify_and_get_experiment

from .forms import DataSchemaConstraintForm, DataSchemaFieldForm
from .models import DataSchemaField
from .tasks import task_write_data_schema

logger = logging.getLogger(__name__)


class DataSchemaOverview(View):
    template_name = 'dataschema_manager/dataschemafield_overview.html'

    def get(self, request, experiment_id):
        experiment = verify_and_get_experiment(request, experiment_id)
        context = {}
        data_schema = experiment.schema
        context['data_schema_list'] = data_schema.fields.all()
        context['experiment_id'] = experiment.id
        context['object'] = experiment
        context['object_type'] = experiment.get_object_type()
        context['form'] = DataSchemaFieldForm()
        context['constraint_form'] = DataSchemaConstraintForm()
        context['schema_active'] = True
        logger.debug('data schema overview for: %s', experiment)
        return render(request, self.template_name, context)


@login_required
def dataschemafield_new(request, experiment_id):
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
                data_schema = experiment.schema
                data_schema.fields.add(edit_form.instance)
                data_schema.save()
            logger.debug('new data schema created for %s: %s', experiment, data_schema)
            return redirect(to=experiment.success_url_dict(hash='#edit')['schema'])
        else:
            context['form'] = edit_form
            context['constraint_form'] = constraint_form
            context['experiment_id'] = experiment_id
            context['edit'] = False
            logger.debug('invalid data schema form for %s: %s', experiment, context)
            return render(request, 'dataschema_manager/dataschemafield_edit.html', context)


@login_required
def dataschemafield_edit(request, pk, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    dataschema = DataSchemaField.objects.get(pk=pk)
    constraints = dataschema.constraints
    context = {'schema_id': dataschema.pk, 'experiment_id': experiment.id}
    if request.POST:
        edit_form = DataSchemaFieldForm(request.POST, instance=dataschema)
        constraint_form = DataSchemaConstraintForm(request.POST, instance=constraints)
        if edit_form.is_valid() and constraint_form.is_valid():
            constraints.save()
            dataschema.constraint = constraints
            dataschema.save()
            logger.debug('edit data schema for %s: %s', experiment, dataschema)
            return redirect(to=experiment.success_url_dict(hash='#edit')['schema'])
        else:
            context['form'] = edit_form
            context['constraint_form'] = constraint_form
            return render(request, 'dataschema_manager/dataschemafield_edit.html', context)
    else:
        context['form'] = DataSchemaFieldForm(instance=dataschema)
        context['constraint_form'] = DataSchemaConstraintForm(instance=constraints)
        return render(request, 'dataschema_manager/dataschemafield_edit.html', context)


@login_required
def dataschema_write(request, experiment_id):
    experiment = verify_and_get_experiment(request, experiment_id)
    task_write_data_schema.delay(experiment_id)
    send_message(request.user.username, MessageStatus.INFO, 'Task started to update data schema...')
    logger.debug('started updating schema for: %s', experiment)
    return JsonResponse({'success': True})
