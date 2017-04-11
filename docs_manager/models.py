from django.db import models
from experiments_manager.models import Experiment


class Docs(models.Model):
    experiment = models.ForeignKey(to=Experiment)
    enabled = models.BooleanField(default=False)
    
