from django.db import models


class AbstractWorker(models.Model):
    AVAILABLE = 'AV'
    NOT_AVAILABLE = 'NO'
    BUSY = 'BU'
    UNKNOWN = 'UN'
    DOWN = 'DO'
    ERROR = 'ER'
    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (NOT_AVAILABLE, 'Not available'),
        (BUSY, 'Busy'),
        (UNKNOWN, 'Unknown'),
        (DOWN, 'Offline'),
        (ERROR, 'Error'),
    )
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    last_ping = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=UNKNOWN)
    communication_key = models.CharField(max_length=200)

    class Meta:
        abstract = True