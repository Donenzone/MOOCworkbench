from django import forms
from django.forms import ModelForm, Textarea, TextInput

from .models import DataSchemaConstraints, DataSchemaField


class JsonTableSchemaNameField(forms.CharField):
    def to_python(self, value):
        return value.lower()


class DataSchemaFieldForm(ModelForm):
    name = JsonTableSchemaNameField(max_length=100)

    class Meta:
        model = DataSchemaField
        fields = ('name', 'datatype', 'primary_key', 'title', 'description',)

        widgets = {
            "title": TextInput(attrs={'placeholder': 'Title of field'}),
            "description": Textarea(attrs={'placeholder': 'Description of the contents of the field'}),
        }


class DataSchemaConstraintForm(ModelForm):

    class Meta:
        model = DataSchemaConstraints
        fields = '__all__'
        widgets = {
            "format": TextInput(attrs={'placeholder': 'Define a format'}),
            "minimum": TextInput(attrs={'placeholder': 'Set the minimum value'}),
            "maximum": TextInput(attrs={'placeholder': 'Set the maximum value'}),
            "min_length": TextInput(attrs={'placeholder': 'Set the minimum length of input'}),
            "max_length": TextInput(attrs={'placeholder': 'Set the maximum length of input'}),
        }
