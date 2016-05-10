from django.db import models
from UserManager.models import WorkbenchUser
from GitManager.models import GitRepository


# Create your models here.
class AbstractExperiment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=200)
    added = models.DateField()
    owner = models.ForeignKey(to=WorkbenchUser)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Script(AbstractExperiment):
    type = 'script'


class Experiment(AbstractExperiment):
    git_repo = models.ForeignKey(to=GitRepository)
    type = 'experiment'
