from django.db import models
from UserManager.models import WorkbenchUser


# Create your models here.
class GitRepository(models.Model):
    title = models.CharField(max_length=200)
    git_url = models.CharField(max_length=100)
    owner = models.ForeignKey(to=WorkbenchUser)
    subrepos = models.ManyToManyField(to='GitRepository', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    github_id = models.IntegerField(null=True)
    hooks_url = models.CharField(max_length=100, null=True)


class GitHubAuth(models.Model):
    state = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True)
    auth_token = models.CharField(max_length=100, null=True)
    workbench_user = models.OneToOneField(to=WorkbenchUser)

class GitRights(models.Model):
    READ = 0
    WRITE = 1
    RW = 2

    rights = (
        (READ, 'Read'),
        (WRITE, 'Write'),
        (RW, 'Read/Write')
    )

    user = models.ForeignKey(to=WorkbenchUser)
    repo = models.ForeignKey(to=GitRepository)
    rights = models.CharField(choices=rights, max_length=2, default=READ)
