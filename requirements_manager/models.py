from django.db import models
from model_utils.models import TimeStampedModel


class Requirement(TimeStampedModel):
    package_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255, null=True)
    package = models.ForeignKey('marketplace.InternalPackage', null=True)

    def __str__(self):
        if self.version is not None:
            return '{0}=={1}'.format(self.package_name, self.version)
        return '{0}'.format(self.package_name)
