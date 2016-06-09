import django_tables2 as tables
from .models import *


class ExperimentTable(tables.Table):
    class Meta:
        model = Experiment
        
        attrs = {'class': 'table'}