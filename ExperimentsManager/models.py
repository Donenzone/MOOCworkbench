from django.db import models
from UserManager.models import WorkbenchUser
from GitManager.models import GitRepository
from WorkerManager.models import Worker
from ExperimentHelper.models import AbstractExperimentRun
from rest_framework.renderers import JSONRenderer
from ExperimentsManager.serializer import serializer_experiment_run_factory
import requests
from helpers.url_helper import build_url


class AbstractExperiment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=200)
    added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(to=WorkbenchUser)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Script(AbstractExperiment):
    type = 'script'


class Experiment(AbstractExperiment):
    git_repo = models.ForeignKey(to=GitRepository, null=True)
    type = 'experiment'


class ExperimentRun(AbstractExperimentRun):
    experiment = models.ForeignKey(to=Experiment)
    owner = models.ForeignKey(to=WorkbenchUser)

    def __str__(self):
        return "ExperimentRun from {0} created at {1} with current status {2}".format(self.owner, self.created, self.status)

    def submit(self):
        self.status = self.BUSY
        self.save()
        serializer = serializer_experiment_run_factory(ExperimentWorkerRun)(self)
        json = JSONRenderer().render(serializer.data)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        requests.post(build_url(self.location, ['api', 'worker', 'experiment-run'], 'POST'), data=json, headers=headers)


class ExperimentWorkerRun(AbstractExperimentRun):
    pass