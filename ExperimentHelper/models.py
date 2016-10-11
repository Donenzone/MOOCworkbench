from django.db import models
from WorkerManager.models import Worker


class AbstractExperimentRun(models.Model):
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
    created = models.DateTimeField(auto_now_add=True)
    output = models.TextField(blank=True)
    selected_worker = models.ForeignKey(to=Worker, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "ExperimentRun for {0} created at {1} with current status {2}".format(self.selected_worker, self.created, self.status)


