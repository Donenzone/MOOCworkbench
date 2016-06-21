from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class WorkbenchUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    netid = models.CharField(max_length=200)
    can_run_experiments = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['netid',]

    def __str__(self):
        return self.user.username


class SSHKeys(models.Model):
    ssh_key = models.CharField(max_length=1000, null=True)
    workbench_user = models.ManyToManyField(to=WorkbenchUser)
