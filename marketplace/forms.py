from django import forms
from django.forms import ModelForm, TextInput

from marketplace.models import InternalPackage


class PackageNameField(forms.CharField):
    def to_python(self, value):
        return value.lower()


class InternalPackageForm(ModelForm):
    class Meta:
        model = InternalPackage
        fields = ['name', 'description', 'category', 'language']

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Package name'}),
        }
