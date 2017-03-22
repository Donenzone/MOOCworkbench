from django.db import models
from ExperimentsManager.models import Experiment


class ExperimentRequirement(models.Model):
    package_name = models.CharField(max_length=255)
    experiment = models.ForeignKey(to=Experiment)
    version = models.CharField(max_length=255, null=True)

    def __str__(self):
        if self.version is not None:
            return '{0}=={1}'.format(package_name, version)
        return '{0}'.format(package_name)
