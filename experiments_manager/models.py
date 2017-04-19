from django.db import models
from django.template.defaultfilters import slugify

from model_utils.models import TimeStampedModel

from user_manager.models import WorkbenchUser
from git_manager.models import GitRepository
from build_manager.models import TravisInstance
from docs_manager.models import Docs
from requirements_manager.models import Requirement


class Experiment(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(to=WorkbenchUser)

    git_repo = models.ForeignKey(to=GitRepository, null=True)
    travis = models.ForeignKey(to=TravisInstance, null=True)
    docs = models.ForeignKey(to=Docs, null=True)
    requirements = models.ManyToManyField(to=Requirement)

    def slug(self):
        return slugify(self.title)


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
