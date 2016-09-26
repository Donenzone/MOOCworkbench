from django.db import models
# Create your models here.


class SubmittedExperiments(models.Model):
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
    submit_date = models.DateTimeField(auto_now_add=True)
    experiment_git_url = models.CharField(max_length=200)
    repo_name = models.CharField(max_length=200)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=CREATED)
    output = models.TextField(blank=True)
    run_id = models.IntegerField()

    def append_to_output(self, line):
        output = self.output
        output += str(line) + '\n'
        self.output = output
        self.save()


class WorkerInformation(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True)
