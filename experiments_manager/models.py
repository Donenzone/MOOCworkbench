from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver

from user_manager.models import WorkbenchUser
from git_manager.models import GitRepository
from build_manager.models import TravisInstance, TravisCiConfig
from docs_manager.models import Docs
from requirements_manager.models import Requirement
from helpers.helper_mixins import ExperimentPackageTypeMixin


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

    def get_absolute_url(self):
        return reverse('experiment_detail', kwargs={'pk': self.pk, 'slug': self.slug()})

    def get_docs_folder(self):
        return [x.folder_name() for x in ChosenExperimentSteps.objects.filter(experiment=self).order_by('step_nr')]

    def get_object_type(self):
        return ExperimentPackageTypeMixin.EXPERIMENT_TYPE

    def get_active_step(self):
        return ChosenExperimentSteps.objects.get(experiment=self, active=True)


@receiver(post_save, sender=Experiment)
def add_experiment_config(sender, instance, created, **kwargs):
    if created:
        docs = Docs()
        docs.save()
        instance.docs = docs

        travis_config = TravisCiConfig()
        travis_config.save()
        travis = TravisInstance(config=travis_config)
        travis.save()
        instance.travis = travis

        instance.save()


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
    started_at = models.DateTimeField()
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)

    def folder_name(self):
        return slugify(self.step.name).replace('-', '_')


def delete_existing_chosen_steps(experiment):
    ChosenExperimentSteps.objects.filter(experiment=experiment).delete()
