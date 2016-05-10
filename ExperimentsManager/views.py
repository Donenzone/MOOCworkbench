from django.shortcuts import render
from rest_framework import viewsets
from ExperimentsManager.serializer import *


# Create your views here.
class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all().order_by('-created')
    serializer_class = ExperimentSerializer


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = Script.objects.all().order_by('-created')
    serializer_class = ScriptSerializer


def index(request):
    return render(request, 'index.html')