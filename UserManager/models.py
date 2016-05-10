from django.db import models
from django.contrib.auth.models import AbstractBaseUser
# Create your models here.


class WorkbenchUser(AbstractBaseUser):
    netid = models.CharField(max_length=200)
    can_run_experiments = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['netid',]



