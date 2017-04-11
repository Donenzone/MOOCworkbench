from django.db import models
from experiments_manager.models import Experiment
from model_utils.models import TimeStampedModel


class ExperimentRequirement(TimeStampedModel):
    package_name = models.CharField(max_length=255)
    experiment = models.ForeignKey(to=Experiment)
    version = models.CharField(max_length=255, null=True)

    def __str__(self):
        if self.version is not None:
            return '{0}=={1}'.format(self.package_name, self.version)
        return '{0}'.format(self.package_name)

    class Meta:
        unique_together = ('package_name', 'experiment')
