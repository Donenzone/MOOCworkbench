from django.shortcuts import render
import requirements
from .models import ExperimentRequirement
from ExperimentsManager.models import Experiment
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.core import serializers
# Create your views here.

def parse_requirements_file(requirements_file):
    for req in requirements.parse(requirements_file):
        print(req.name, req.specs, req.extras)


@login_required
def experiment_list_view(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    data = serializers.serialize('json', ExperimentRequirement.objects.filter(experiment=experiment))
    return JsonResponse({'requirements': data})


@login_required
def add_experiment_requirement(request, experiment_id):
    assert request.POST
    assert request.POST['package_name']
    assert request.POST['version']
    package_name = request.POST['package_name']
    version = request.POST['version']

    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user

    requirement = ExperimentRequirement(package_name=package_name, experiment=experiment, version=version)
    requirement.save()
    return JsonResponse({'added': True})


@login_required
def remove_experiment_requirement(request, experiment_id, requirement_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    requirement = ExperimentRequirement.objects.get(id=requirement_id)
    requirement.delete()


@login_required
def write_requirements_file(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    assert experiment.owner.user == request.user
    requirements_txt = ''
    for requirement in ExperimentRequirement.objects.filter(experiment=experiment):
        requirements_txt += str(requirement)
    return requirements_txt
