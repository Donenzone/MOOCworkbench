from django.db import models
from UserManager.models import WorkbenchUser
from GitManager.models import GitRepository
from rest_framework.renderers import JSONRenderer
from ExperimentsManager.serializer import serializer_experiment_run_factory
import requests
from helpers.url_helper import build_url
from model_utils.models import TimeStampedModel
from django.template.defaultfilters import slugify


class AbstractExperiment(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=200)
    added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(to=WorkbenchUser)

    class Meta:
        abstract = True


class Script(AbstractExperiment):
    type = 'script'


class Experiment(AbstractExperiment):
    git_repo = models.ForeignKey(to=GitRepository, null=True)
    type = 'experiment'


class ExperimentStep(models.Model):
    step_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    default_order = models.IntegerField()

    def __str__(self):
        return self.step_name

class ChosenExperimentSteps(models.Model):
    step = models.ForeignKey(to=ExperimentStep)
    experiment = models.ForeignKey(to=Experiment)
    step_nr = models.IntegerField()
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def folder_name(self):
        return slugify(self.step.step_name).replace('-', '_')

def delete_existing_chosen_steps(experiment):
    ChosenExperimentSteps.objects.filter(experiment=experiment).delete()
