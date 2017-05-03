from django import forms
from django.forms import ModelForm
from django.forms import TextInput, Textarea

from .models import DataSchemaField, DataSchemaConstraints


class DataSchemaFieldForm(ModelForm):
    unique = forms.BooleanField(label='Field has to be unique', required=False)
    required = forms.BooleanField(label='Field is required', required=False)
    format = forms.CharField(help_text='Format of value', required=False)
    minimum = forms.CharField(help_text='Minimum value', required=False)
    maximum = forms.CharField(help_text='Maximum value', required=False)
    min_length = forms.CharField(help_text='Minimum length of value', required=False)
    max_length = forms.CharField(help_text='Maximum length of value', required=False)

    class Meta:
        model = DataSchemaField
        fields = ('name', 'datatype', 'primary_key', 'title', 'description',)

        widgets = {
            "name": TextInput(attrs={'placeholder': 'Name of field'}),
            "title": TextInput(attrs={'placeholder': 'Title of field'}),
            "description": Textarea(attrs={'placeholder': 'Description of the contents of the field'}),
        }
