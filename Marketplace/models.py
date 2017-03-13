from django.db import models
from UserManager.models import WorkbenchUser
from markdownx.models import MarkdownxField

class Package(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    internal_package = models.BooleanField(default=False)
    project_page = models.URLField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PackageVersion(models.Model):
    package = models.ForeignKey(to=Package)
    version_nr = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    changelog = models.TextField()
    added_by = models.ForeignKey(to=WorkbenchUser)
    url = models.URLField()

class PackageResource(models.Model):
    package = models.ForeignKey(to=Package)
    resource = MarkdownxField()
    url = models.URLField(null=True)
    added_by = models.ForeignKey(to=WorkbenchUser)
    created = models.DateTimeField(auto_now_add=True)
