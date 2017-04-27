from django import forms

from cookiecutter_manager.models import CookieCutterTemplate
from .models import *


class ExperimentForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=True)
    template = forms.ModelChoiceField(queryset=CookieCutterTemplate.objects.filter(meant_for=CookieCutterTemplate.EXPERIMENT))

    class Meta:
        model = Experiment
        fields = ('title', 'description', 'template')
