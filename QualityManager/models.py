from django.db import models
from ExperimentsManager.models import Experiment
from model_utils.models import TimeStampedModel
# Create your models here.

class ExperimentMeasure(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    high_message = models.CharField(max_length=255, default='High')
    medium_message = models.CharField(max_length=255, default='Medium')
    low_message = models.CharField(max_length=255, default='Low')

    def __str__(self):
        return 'Measurement of {0}'.format(self.name)


class RawMeasureResult(models.Model):
    key = models.CharField(max_length=255)
    value = models.FloatField(max_length=255)

    def __str__(self):
        return 'Key: {0} with value: {1}'.format(self.key, str(self.value))

class ExperimentMeasureResult(TimeStampedModel):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'

    SCALE = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    experiment = models.ForeignKey(to=Experiment)
    measurement = models.ForeignKey(to=ExperimentMeasure)
    result = models.CharField(max_length=1, choices=SCALE)
    raw_values = models.ManyToManyField(to=RawMeasureResult)


    def get_message(self):
        message_dict = {ExperimentMeasureResult.LOW: self.measurement.low_message,
                ExperimentMeasureResult.MEDIUM: self.measurement.medium_message,
                ExperimentMeasureResult.HIGH: self.measurement.high_message}
        return message_dict[self.result]
