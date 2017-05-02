from django.shortcuts import render
from django.views.generic import CreateView
from django.db import transaction

from experiments_manager.helper import verify_and_get_experiment

from .models import DataSchemaField
from .forms import DataSchemaFieldForm
from .mixins import DataSchemaFieldListMixin


class DataSchemaFieldCreateView(DataSchemaFieldListMixin, CreateView):
    model = DataSchemaField
    form_class = DataSchemaFieldForm

    def form_valid(self, form):
        experiment = verify_and_get_experiment(self.request, self.kwargs['experiment_id'])
        with transaction.atomic():
            response = super(DataSchemaFieldCreateView, self).form_valid(form)
            experiment.schema.add(form.instance)
            experiment.save()
        return response

    def get_success_url(self):
        return '/experiments/7/sandbox-experiment/#schema'
