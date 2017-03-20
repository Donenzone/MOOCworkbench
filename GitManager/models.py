from django.db import models
from UserManager.models import WorkbenchUser

# Create your models here.
class GitRepository(models.Model):
    name = models.CharField(max_length=200)
    has_issues = models.BooleanField(default=True)
    has_wiki = models.BooleanField(default=True)
    github_url = models.URLField()
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(to=WorkbenchUser)
    created = models.DateTimeField(auto_now_add=True)
    hooks_url = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
