from django.db import models
from ExperimentsManager.models import Experiment
# Create your models here.

class ExperimentMeasure(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

HIGH = 'H'
MEDIUM = 'M'
LOW = 'L'

class ExperimentMeasureResult(models.Model):
    SCALE = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    experiment = models.ForeignKey(to=Experiment)
    measurement = models.ForeignKey(to=ExperimentMeasure)
    result = models.CharField(max_length=1, choices=SCALE)
    performed_at = models.DateTimeField(auto_now_add=True)
