from django.db import models
from user_manager.models import WorkbenchUser
from model_utils.models import TimeStampedModel


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_point = models.TextField()
    end_point = models.TextField(null=True)
    for_model = models.CharField(max_length=255, null=True)
    active = models.BooleanField(default=True)
    dependent_on = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.name


class feedback(models.Model):
    like = models.BooleanField(verbose_name="Overall, was your experience positive?")
    feedback_like = models.TextField(null=True, verbose_name="What did you like about your experience?")
    feedback_dislike = models.TextField(null=True, verbose_name="What didn't you like about your experience?")
    other_comments = models.TextField(null=True, verbose_name="Do you have any other comments?")
    for_task = models.ForeignKey(to=Task, null=True)


class UserTask(TimeStampedModel):
    for_task = models.ForeignKey(to=Task)
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    left_feedback = models.BooleanField(default=False)
    user = models.ForeignKey(to=WorkbenchUser)
