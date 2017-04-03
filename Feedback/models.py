from django.db import models
from UserManager.models import WorkbenchUser
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

class Feedback(models.Model):
    like = models.BooleanField()
    feedback_like = models.TextField(null=True)
    feedback_dislike = models.TextField(null=True)
    other_comments = models.TextField(null=True)
    for_task = models.ForeignKey(to=Task, null=True)

class UserTask(TimeStampedModel):
    for_task = models.ForeignKey(to=Task)
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    left_feedback = models.BooleanField(default=False)
    user = models.ForeignKey(to=WorkbenchUser)
