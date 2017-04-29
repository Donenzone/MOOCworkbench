from django.db import models


class PylintScan(models.Model):
    enabled = models.BooleanField(default=True)
    last_scan = models.DateTimeField(null=True)


class PylintScanResult(models.Model):
    for_project = models.ForeignKey(to=PylintScan)
    scanned_at = models.DateTimeField(auto_now_add=True)
    nr_of_errors = models.IntegerField(default=0)
    nr_of_warnings = models.IntegerField(default=0)
    nr_of_other_issues = models.IntegerField(default=0)


class PylintResult(models.Model):
    for_result = models.ForeignKey(to=PylintScanResult)
    pylint_type = models.CharField(max_length=1)
    message = models.CharField(max_length=100)
    line_nr = models.IntegerField()
    file_path = models.CharField(max_length=100)

