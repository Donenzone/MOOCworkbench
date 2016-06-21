from django import forms
from .models import *


class ExperimentForm(forms.ModelForm):
    new_git_repo = forms.BooleanField(required=False, label="Create new Git repository")
    git_repo = forms.ModelChoiceField(required=False, queryset=GitRepository.objects.all())
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Experiment
        fields = ('title', 'description', 'git_repo')
