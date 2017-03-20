from django import forms
from .models import *


class ExperimentForm(forms.ModelForm):
    new_git_repo = forms.BooleanField(required=False, label="Create new GitHub repository", initial=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Experiment
        fields = ('title', 'description')
