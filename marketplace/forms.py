from django.forms import ModelForm
from django.forms import TextInput

from marketplace.models import InternalPackage


class InternalPackageForm(ModelForm):
    class Meta:
        model = InternalPackage
        fields = ['name', 'description', 'category', 'language']

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Package name'}),
        }
