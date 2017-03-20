from django.db import models
from UserManager.models import WorkbenchUser

# Create your models here.
class GitRepository(models.Model):
    title = models.CharField(max_length=200)
    github_url = models.CharField(max_length=100)
    owner = models.ForeignKey(to=WorkbenchUser)
    created = models.DateTimeField(auto_now_add=True)
    github_id = models.IntegerField(null=True)
    hooks_url = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title
