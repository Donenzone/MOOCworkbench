from django.db import models
from model_utils.models import TimeStampedModel

from user_manager.models import WorkbenchUser


class Commit(models.Model):
    sha_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    commit_message = models.CharField(max_length=1000)
    username = models.CharField(max_length=255)
    additions = models.IntegerField(null=True)
    deletions = models.IntegerField(null=True)
    total = models.IntegerField(null=True)


class GitRepository(TimeStampedModel):
    name = models.CharField(max_length=200)
    has_issues = models.BooleanField(default=True)
    has_wiki = models.BooleanField(default=True)
    github_url = models.URLField()
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(to=WorkbenchUser)
    hooks_url = models.CharField(max_length=100, null=True)
    commits = models.ManyToManyField(to=Commit)

    def __str__(self):
        return self.name
