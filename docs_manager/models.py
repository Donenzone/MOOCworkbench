from django.db import models


class Docs(models.Model):
    enabled = models.BooleanField(default=False)
    
