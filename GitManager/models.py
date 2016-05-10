from django.db import models
from UserManager.models import WorkbenchUser


# Create your models here.
class GitRepository(models.Model):
    title = models.CharField(max_length=200)
    git_url = models.CharField(max_length=200)
    owner = models.ForeignKey(to=WorkbenchUser)
    subrepos = models.ManyToManyField(to='GitRepository', blank=True)
    created = models.DateTimeField(auto_now_add=True)