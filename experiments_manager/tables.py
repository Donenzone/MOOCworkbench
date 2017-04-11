import django_tables2 as tables
from .models import *
from django_tables2.utils import A


class ExperimentTable(tables.Table):
    title = tables.LinkColumn('experiment_detail', text=lambda record: record.title, args=[A('pk'), A('slug')])

    class Meta:
        model = Experiment
        attrs = {'class': 'table'}
