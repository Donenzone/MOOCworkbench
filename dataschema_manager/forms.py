"""Forms for DataSchema app"""
from django import forms
from django.forms import ModelForm, Textarea, TextInput

from .models import DataSchemaConstraints, DataSchemaField


class JsonTableSchemaNameField(forms.CharField):
    """A special form field for JSON Table Schema,
    that requires the name field to be all lowercase"""
    def to_python(self, value):
        return value.lower()


class DataSchemaFieldForm(ModelForm):
    """Form for adding a DataSchemaField"""
    name = JsonTableSchemaNameField(max_length=100)

    class Meta:
        model = DataSchemaField
        fields = ('name', 'datatype', 'primary_key', 'title', 'description',)

        widgets = {
            "title": TextInput(attrs={'placeholder': 'Title of field'}),
            "description": Textarea(attrs={'placeholder': 'Description of the contents of the field'}),
        }


class DataSchemaConstraintForm(ModelForm):
    """Form for adding a DataSchemaConstraint, part of a DataSchemaField"""

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
