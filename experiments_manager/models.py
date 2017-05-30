from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from model_utils.models import TimeStampedModel

from build_manager.models import TravisCiConfig, TravisInstance
from coverage_manager.models import CodeCoverage
from dataschema_manager.models import DataSchema
from docs_manager.models import Docs
from git_manager.helpers.language_helper import PythonHelper, RHelper
from git_manager.models import GitRepository
from helpers.helper_mixins import ExperimentPackageTypeMixin
from marketplace.models import BasePackage
from pylint_manager.models import PylintScan
from requirements_manager.models import Requirement
from user_manager.models import WorkbenchUser


class Experiment(BasePackage):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(to=WorkbenchUser)
    template = models.ForeignKey('cookiecutter_manager.CookieCutterTemplate')
    completed = models.BooleanField(default=False)
    unique_id = models.CharField(max_length=100, null=True)
    public = models.BooleanField(default=False)
    publish_url_zip = models.URLField(null=True)

    git_repo = models.ForeignKey(to=GitRepository, null=True)
    travis = models.ForeignKey(to=TravisInstance, null=True)
    docs = models.ForeignKey(to=Docs, null=True)
    requirements = models.ManyToManyField(to=Requirement)
    pylint = models.ForeignKey(to=PylintScan, null=True)
    schema = models.ForeignKey(to=DataSchema, null=True)

    def slug(self):
        return slugify(self.title)

    def get_absolute_url(self, tab=None):
        if self.completed:
            return reverse('experiment_readonly', kwargs={'unique_id': self.unique_id})
        return reverse('experiment_detail', kwargs={'pk': self.pk, 'slug': self.slug()})

    def get_docs_folder(self):
        return [x.location for x in ChosenExperimentSteps.objects.filter(experiment=self).order_by('step_nr')]

    def get_object_type(self):
        return ExperimentPackageTypeMixin.EXPERIMENT_TYPE

    def get_active_step(self):
        active_step = ChosenExperimentSteps.objects.filter(experiment=self, active=True)
        if active_step:
            return active_step[0]

    def delete(self, using=None, keep_parents=False):
        if self.docs:
            self.docs.delete()
        if self.git_repo:
            self.git_repo.delete()
        if self.travis.codecoverage_set:
            coverage = self.travis.codecoverage_set.first()
            coverage.delete()
        if self.travis:
            self.travis.delete()
        if self.pylint:
            self.pylint.delete()
        if self.schema:
            self.schema.delete()
        super(Experiment, self).delete()

    def __str__(self):
        return self.title

    def get_activity_message(self):
        message = "Experiment {0} by {1} was completed"
        if self.public:
            message = "Experiment {0} by {1} was completed and made public"
        return message.format(self.title, self.owner)

    def success_url_dict(self, hash=''):
        return {'dependencies': reverse('experiment_dependencies', kwargs={'pk': self.pk,
                                                                           'object_type': self.get_object_type()})
                                                                            + hash,
                'resources': '',
                'versions': '',
                'schema': reverse('experiment_schema', kwargs={'experiment_id': self.pk}) + hash,
                'detail': self.get_absolute_url() + hash}

    def language_helper(self):
        language_helper_dict = {'Python3': PythonHelper, 'R': RHelper}
        return language_helper_dict[self.template.language.language](self)


@receiver(post_save, sender=Experiment)
def add_experiment_config(sender, instance, created, **kwargs):
    if created:
        docs = Docs()
        docs.enabled = True
        docs.save()
        instance.docs = docs

        travis_config = TravisCiConfig()
        travis_config.save()
        travis = TravisInstance(config=travis_config)
        travis.save()
        instance.travis = travis

        coverage = CodeCoverage()
        coverage.travis_instance = travis
        coverage.enabled = False
        coverage.save()

        pylint = PylintScan()
        pylint.enabled = True
        pylint.save()
        instance.pylint = pylint

        schema = DataSchema(name='main')
        schema.save()
        instance.schema = schema

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
