from django.db import models
from django.contrib.auth.models import User, Group
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils.models import TimeStampedModel


class WorkbenchUser(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    netid = models.CharField(max_length=200)
    can_run_experiments = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['netid',]

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('view_profile', kwargs={'username': self.user.username})


def get_workbench_user(user):
    return WorkbenchUser.objects.get(user=user)


@receiver(post_save, sender=User)
def create_workbench_user(sender, instance, created, **kwargs):
    if created:
        workbench_user = WorkbenchUser.objects.filter(user=instance)
        if not workbench_user:
            new_workbench_user = WorkbenchUser(user=instance, netid='superuser')
            new_workbench_user.save()


def get_researcher_group():
    return Group.objects.get(name='Researcher')