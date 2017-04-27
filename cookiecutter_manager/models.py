from django.db import models


class CookieCutterTemplate(models.Model):
    EXPERIMENT = 'e'
    PACKAGE = 'p'
    MEANT_FOR_CHOICES = (
        (EXPERIMENT, 'Experiment'),
        (PACKAGE, 'Package')
    )
    location = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    meant_for = models.CharField(choices=MEANT_FOR_CHOICES, default=EXPERIMENT, max_length=10)

    def __str__(self):
        return self.name
