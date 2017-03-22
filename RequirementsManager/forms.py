from django.forms import ModelForm
from .models import ExperimentRequirement
from django.forms import TextInput

class ExperimentRequirementForm(ModelForm):
    class Meta:
        model = ExperimentRequirement
        fields = ['package_name', 'version']

        widgets = {
            'package_name': TextInput(attrs={'placeholder': 'Package name'}),
            'version': TextInput(attrs={'placeholder': 'Version nr.'}),
        }
