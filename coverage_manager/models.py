from django.db import models

from build_manager.models import TravisInstance


class CodeCoverage(models.Model):
    """CodeCoverage model, contains reference to Travis, because only then can
    code coverage be enabled. Also has the url to the badge and a boolean indicating
    if code coverage measurements are enabled or not"""
    travis_instance = models.ForeignKey(to=TravisInstance)
    badge_url = models.URLField(null=True)
    enabled = models.BooleanField(default=True)
