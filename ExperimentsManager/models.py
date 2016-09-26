from django.db import models
from UserManager.models import WorkbenchUser
from GitManager.models import GitRepository
from WorkerManager.models import Worker


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


class ExperimentRun(models.Model):
    CREATED = 'CR'
    RUNNING = 'RU'
    SUCCESS = 'SU'
    ERROR = 'ER'
    CANCELLED = 'CA'
    STATUS_CHOICES = (
        (CREATED, 'Created'),
        (RUNNING, 'Running'),
        (SUCCESS, 'Success'),
        (ERROR, 'Error'),
        (CANCELLED, 'Cancelled'),
    )

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=CREATED)
    experiment = models.ForeignKey(to=Experiment)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(to=WorkbenchUser)
    output = models.TextField(blank=True)
    selected_worker = models.ForeignKey(to=Worker, null=True)

    def append_to_output(self, line):
        output = self.output
        output += line + '\n'
        self.output = output
        self.save()