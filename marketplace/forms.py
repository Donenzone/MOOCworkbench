from markdownx.fields import MarkdownxFormField
from markdownx.widgets import MarkdownxWidget

from django import forms
from django.forms import ModelForm
from django.forms import TextInput

from marketplace.models import InternalPackage, PackageResource


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

