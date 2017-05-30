from django.db import models
from django.template.defaultfilters import slugify
from model_utils.models import TimeStampedModel

from experiments_manager.models import ChosenExperimentSteps


class ExperimentMeasure(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    high_message = models.CharField(max_length=255, default='High')
    medium_message = models.CharField(max_length=255, default='Medium')
    low_message = models.CharField(max_length=255, default='Low')

    def __str__(self):
        return 'Measurement of {0}'.format(self.name)

    def get_low_message(self):
        return '{0}: {1}'.format(self.name, self.low_message)

    def get_medium_message(self):
        return '{0}: {1}'.format(self.name, self.medium_message)

    def get_high_message(self):
        return '{0}: {1}'.format(self.name, self.high_message)

    def slug(self):
        return slugify(self.name).replace('-', '_')


class RawMeasureResult(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=1000)

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
    step = models.ForeignKey(to=ChosenExperimentSteps)
    measurement = models.ForeignKey(to=ExperimentMeasure)
    result = models.CharField(max_length=1, choices=SCALE)
    raw_values = models.ManyToManyField(to=RawMeasureResult)

    def get_message(self):
        message_dict = {ExperimentMeasureResult.LOW: self.measurement.get_low_message(),
                ExperimentMeasureResult.MEDIUM: self.measurement.get_medium_message(),
                ExperimentMeasureResult.HIGH: self.measurement.get_high_message()}
        if self.result:
            return message_dict[self.result]
        return 'Result missing'

    def get_class(self):
        style_classes = {ExperimentMeasureResult.LOW: 'danger',
                ExperimentMeasureResult.MEDIUM: 'warning',
                ExperimentMeasureResult.HIGH: 'success'}
        if not self.result:
            return "default"
        return style_classes[self.result]

    def slug(self):
        return self.measurement.slug()

    def __str__(self):
        return "Workbench scan of {0}".format(self.measurement.name)
