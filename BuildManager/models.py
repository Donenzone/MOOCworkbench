from django.db import models
from ExperimentsManager.models import Experiment
# Create your models here.

class TravisInstance(models.Model):
    experiment = models.ForeignKey(to=Experiment)
    build_status = models.CharField(max_length=20)
