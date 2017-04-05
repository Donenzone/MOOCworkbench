from django.db import models
from ExperimentsManager.models import Experiment


class Docs(models.Model):
    experiment = models.ForeignKey(to=Experiment)
    enabled = models.BooleanField(default=False)
    
