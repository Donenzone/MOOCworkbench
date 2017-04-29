from django.db import models


class PylintScan(models.Model):
    enabled = models.BooleanField(default=True)
    last_scan = models.DateTimeField(null=True)

    def __str__(self):
        return "PylintScan: {0}".format(self.enabled)


class PylintScanResult(models.Model):
    for_project = models.ForeignKey(to=PylintScan)
    scanned_at = models.DateTimeField(auto_now_add=True)
    nr_of_errors = models.IntegerField(default=0)
    nr_of_warnings = models.IntegerField(default=0)
    nr_of_other_issues = models.IntegerField(default=0)

    def __str__(self):
        return "Scan results for {0}, nr of issues (e,w,c): {1}, {2}, {3}".format(
            self.for_project,
            self.nr_of_errors,
            self.nr_of_warnings,
            self.nr_of_other_issues
        )


class PylintResult(models.Model):
    for_result = models.ForeignKey(to=PylintScanResult)
    pylint_type = models.CharField(max_length=1)
    message = models.CharField(max_length=100)
    line_nr = models.IntegerField()
    file_path = models.CharField(max_length=100)

    def __str__(self):
        return "Type {0} for line nr {1}".format(self.pylint_type, self.line_nr)
