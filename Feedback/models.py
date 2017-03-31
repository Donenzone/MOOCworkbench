from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_point = models.TextField()
    end_point = models.TextField(null=True)
    for_model = models.CharField(max_length=255, null=True)

class Feedback(models.Model):
    like = models.BooleanField()
    feedback_like = models.TextField(null=True)
    feedback_dislike = models.TextField(null=True)
    other_comments = models.TextField(null=True)
    for_task = models.ForeignKey(to=Task, null=True)
