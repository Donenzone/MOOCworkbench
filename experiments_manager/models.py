from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver

from build_manager.models import TravisInstance, TravisCiConfig
from dataschema_manager.models import DataSchema
from docs_manager.models import Docs
from git_manager.models import GitRepository
from helpers.helper_mixins import ExperimentPackageTypeMixin
from marketplace.models import BasePackage
from pylint_manager.models import PylintScan
from requirements_manager.models import Requirement
from user_manager.models import WorkbenchUser
from git_manager.helpers.language_helper import PythonHelper, RHelper


class Experiment(BasePackage):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(to=WorkbenchUser)
    template = models.ForeignKey('cookiecutter_manager.CookieCutterTemplate')
    completed = models.BooleanField(default=False)

    git_repo = models.ForeignKey(to=GitRepository, null=True)
    travis = models.ForeignKey(to=TravisInstance, null=True)
    docs = models.ForeignKey(to=Docs, null=True)
    requirements = models.ManyToManyField(to=Requirement)
    pylint = models.ForeignKey(to=PylintScan, null=True)
    schema = models.ManyToManyField(to=DataSchema)

    def slug(self):
        return slugify(self.title)

    def get_absolute_url(self, tab=None):
        absolute_url = reverse('experiment_detail', kwargs={'pk': self.pk, 'slug': self.slug()})
        if tab:
            absolute_url = '{0}#{1}'.format(absolute_url, tab)
        return absolute_url

    def get_docs_folder(self):
        return [x.location for x in ChosenExperimentSteps.objects.filter(experiment=self).order_by('step_nr')]

    def get_object_type(self):
        return ExperimentPackageTypeMixin.EXPERIMENT_TYPE

    def get_active_step(self):
        active_step = ChosenExperimentSteps.objects.filter(experiment=self, active=True)
        if active_step:
            return active_step[0]

    def __str__(self):
        return self.title

    def success_url_dict(self):
        return {'dependencies': reverse('package_dependencies', kwargs={'pk': self.pk, 'object_type': self.get_object_type()}),
                'resources': '',
                'versions': ''}

    def language_helper(self):
        language_helper_dict = {'Python3': PythonHelper, 'R': RHelper}
        return language_helper_dict[self.template.language.language](self)


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

        pylint = PylintScan()
        pylint.save()
        instance.pylint = pylint

        schema = DataSchema(name='main')
        schema.save()
        instance.schema.add(schema)

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
    started_at = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, blank=True)
    main_module = models.CharField(max_length=100, blank=True)

    def location_slug(self):
        return slugify(self.location)


def delete_existing_chosen_steps(experiment):
    ChosenExperimentSteps.objects.filter(experiment=experiment).delete()
