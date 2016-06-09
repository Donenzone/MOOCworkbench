from django.shortcuts import render
from rest_framework import viewsets
from ExperimentsManager.serializer import *
from django.contrib.auth.decorators import login_required
from .tables import ExperimentTable


# Create your views here.
class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all().order_by('-created')
    serializer_class = ExperimentSerializer


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = Script.objects.all().order_by('-created')
    serializer_class = ScriptSerializer


@login_required
def index(request):
    owner = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=owner)
    table = ExperimentTable(experiments)
    return render(request, 'experiments_table.html', {'table': table})