from django.db import models


class TravisCiConfig(models.Model):
    python_version = models.CharField(max_length=10, default="3.6")


class TravisInstance(models.Model):
    FAILED ='F'
    SUCCESS = 'S'
    CANCELLED = 'C'

    BUILD_STATUS = {
        (FAILED, 'Failed'),
        (SUCCESS, 'Success'),
        (CANCELLED, 'Cancelled')
    }
    last_build_status = models.CharField(max_length=1, choices=BUILD_STATUS, null=True)
    config = models.ForeignKey(to=TravisCiConfig)
    enabled = models.BooleanField(default=True)
