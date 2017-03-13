from django.db import models
from UserManager.models import WorkbenchUser


class Package(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    internal_package = models.BooleanField(default=False)
    project_page = models.URLField()
    created = models.DateTimeField(auto_now_add=True)

class PackageVersion(models.Model):
    version_nr = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    changelog = models.TextField()
    added_by = models.ForeignKey(to=WorkbenchUser)
    url = models.URLField()
    package = models.ForeignKey(to=Package)
