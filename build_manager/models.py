"""Models for build_manager app"""
from django.db import models


class TravisCiConfig(models.Model):
    """Configuration for the Travis instance, for example defining which Python version to be used in builds"""
    python_version = models.CharField(max_length=10, default="3.6")


class TravisInstance(models.Model):
    """Travis Instance model, indicating if builds are enabled or not,
    a TravisCiConfig and the status of the last build"""
    FAILED = 'F'
    SUCCESS = 'S'
    CANCELLED = 'C'

    BUILD_STATUS = {
        (FAILED, 'Failed'),
        (SUCCESS, 'Success'),
        (CANCELLED, 'Cancelled')
    }
    last_build_status = models.CharField(max_length=1, choices=BUILD_STATUS, null=True)
    config = models.ForeignKey(to=TravisCiConfig)
    enabled = models.BooleanField(default=False)
