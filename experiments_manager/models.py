from django.db import models
from user_manager.models import WorkbenchUser
from git_manager.models import GitRepository
from rest_framework.renderers import JSONRenderer
from experiments_manager.serializer import serializer_experiment_run_factory
import requests
from model_utils.models import TimeStampedModel
from django.template.defaultfilters import slugify


class AbstractExperiment(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=200)
    added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(to=WorkbenchUser)

    def slug(self):
        return slugify(self.title)

    class Meta:
        abstract = True


class Script(AbstractExperiment):
    type = 'script'


class Experiment(AbstractExperiment):
    git_repo = models.ForeignKey(to=GitRepository, null=True)
    type = 'experiment'


class ExperimentStep(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    default_order = models.IntegerField()

    def __str__(self):
        return self.name

class ChosenExperimentSteps(models.Model):
    step = models.ForeignKey(to=ExperimentStep)
    experiment = models.ForeignKey(to=Experiment)
    step_nr = models.IntegerField()
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def folder_name(self):
        return slugify(self.step.name).replace('-', '_')

def delete_existing_chosen_steps(experiment):
    ChosenExperimentSteps.objects.filter(experiment=experiment).delete()
