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

    def __str__(self):
        return "Experiment submitted on {0} with run ID {1}, current status: {2}".format(self.submit_date, str(self.run_id), self.status)


class WorkerInformation(models.Model):
    ACCEPT_INCOMING = 1
    DENY_INCOMING = 0

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True)
    status = models.IntegerField(default=ACCEPT_INCOMING)

    def __str__(self):
        return "Worker {0} at {1} with current status {2}".format(self.name, self.location, self.get_current_status())

    def get_current_status(self):
        if self.status == self.DENY_INCOMING:
            return"Not accepting incoming jobs"
        return "Accepting incoming jobs"

