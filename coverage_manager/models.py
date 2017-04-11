from django.db import models
from build_manager.models import TravisInstance


class CodeCoverage(models.Model):
    travis_instance = models.ForeignKey(to=TravisInstance)
    badge_url = models.URLField(null=True)
    enabled = models.BooleanField(default=True)
