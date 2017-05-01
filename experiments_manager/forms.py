from django import forms

from cookiecutter_manager.models import CookieCutterTemplate
from .models import *


class ExperimentForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=True)
    template = forms.ModelChoiceField(queryset=CookieCutterTemplate.objects.filter(meant_for=CookieCutterTemplate.EXPERIMENT))

    class Meta:
        model = Experiment
        fields = ('title', 'description', 'template')


class ExperimentSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super(ExperimentSelectForm, self).__init__(*args, **kwargs)

        self.fields['experiments'].queryset = Experiment.objects.filter(owner__user_id=user_id)

    experiments = forms.ModelChoiceField(queryset=Experiment.objects.filter(completed=False))
