"""Database models for cookiecutter manager"""
from django.db import models

from experiments_manager.models import ExperimentStep
from marketplace.models import Language


class CookieCutterLocationToStepMapping(models.Model):
    """In order to add a Cookiecutter template, add a mapping from the Experiment Steps to
    the location in the new cookiecutter template"""
    location = models.CharField(max_length=100)
    main_module = models.CharField(max_length=100)
    step = models.ForeignKey(to=ExperimentStep)

    def __str__(self):
        return self.location


class CookieCutterTemplate(models.Model):
    """A CookieCutter template, can be added for an experiment or an internal package,
    location points to a remote git repository, and doc_src_location to location
    of docs source files
    :param location: URL to git repository of cookiecutter template"""
    EXPERIMENT = 'e'
    PACKAGE = 'p'
    MEANT_FOR_CHOICES = (
        (EXPERIMENT, 'Experiment'),
        (PACKAGE, 'Package')
    )
    location = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    meant_for = models.CharField(choices=MEANT_FOR_CHOICES, default=EXPERIMENT, max_length=10)
    language = models.ForeignKey(to=Language)
    folder_file_locations = models.ManyToManyField(to=CookieCutterLocationToStepMapping, blank=True)

    docs_src_location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
