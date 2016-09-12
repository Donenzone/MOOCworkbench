from django.db import models
import requests
from helpers.url_helper import build_url
# Create your models here.

class Worker(models.Model):
    AVAILABLE = 'AV'
    NOT_AVAILABLE = 'NO'
    BUSY = 'BU'
    UNKNOWN = 'UN'
    DOWN = 'DO'
    ERROR = 'ER'
    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (NOT_AVAILABLE, 'Not available'),
        (BUSY, 'Busy'),
        (UNKNOWN, 'Unknown'),
        (DOWN, 'Offline'),
        (ERROR, 'Error'),
    )
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    last_ping = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=UNKNOWN)
    communication_key = models.CharField(max_length=200)

    def submit(self, experiment_git_repo_url, repo_name):
        data = {'git_url': experiment_git_repo_url, 'repo_name': repo_name}
        response = requests.post(build_url(self.location, ['worker', 'submit'], 'POST'), data=data)
        self.status = self.BUSY
        self.save()
        return response
