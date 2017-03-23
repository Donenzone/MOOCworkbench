from django.db import models
from ExperimentsManager.models import Experiment
# Create your models here.

class ExperimentQualityMeasure(models.Model):
    MEASUREMENT_TYPES = (
        ('MTZ', 'More than zero'),
        ('')
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=3, choices=MEASUREMENT_TYPES)


class ExperimentQualityResult(models.Model):
    experiment = models.ForeignKey(to=Experiment)
    measurement = models.ForeignKey(to=ExperimentQualityMeasure)
    result = models.FloatField(default=0)
