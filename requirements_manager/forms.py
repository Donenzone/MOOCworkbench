from django.forms import ModelForm
from django.forms import TextInput

from requirements_manager.models import Requirement


class RequirementForm(ModelForm):
    class Meta:
        model = Requirement
        fields = ["package_name", 'version']

        widgets = {
            "package_name": TextInput(attrs={'placeholder': 'Package name'}),
            'version': TextInput(attrs={'placeholder': 'Version nr.'}),
        }
