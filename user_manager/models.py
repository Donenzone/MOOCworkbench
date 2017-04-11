from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class WorkbenchUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    netid = models.CharField(max_length=200)
    can_run_experiments = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['netid',]

    def __str__(self):
        return self.user.username

def get_workbench_user(user):
    return WorkbenchUser.objects.get(user=user)

@receiver(post_save, sender=User)
def create_workbench_user(sender, instance, created, **kwargs):
    if created:
        workbench_user = WorkbenchUser.objects.filter(user=instance)
        if workbench_user.count() == 0:
            new_workbench_user = WorkbenchUser(user=instance, netid='superuser')
            new_workbench_user.save()

class SSHKeys(models.Model):
    ssh_key = models.CharField(max_length=1000, null=True)
    workbench_user = models.ManyToManyField(to=WorkbenchUser)
