from django.db import models

# Create your models here.

class SubmittedExperiments(models.Model):
    RUNNING = 'RU'
    PENDING = 'PE'
    SUCCESS = 'SU'
    FAILED = 'FA'
    CANCELLED = 'CA'
    STATUS_CHOICES = (
        (RUNNING, 'Running'),
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (CANCELLED, 'Cancelled'),
    )
    submit_date = models.DateTimeField(auto_now_add=True)
    experiment_git_url = models.CharField(max_length=200)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)


class WorkerInformation(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True)
