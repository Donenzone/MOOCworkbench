from django import forms
from django.forms import ModelForm
from django.forms import TextInput, Textarea

from .models import DataSchemaField, DataSchemaConstraints


class DataSchemaFieldForm(ModelForm):

    class Meta:
        model = DataSchemaField
        fields = ('name', 'datatype', 'primary_key', 'title', 'description',)

        widgets = {
            "name": TextInput(attrs={'placeholder': 'Name of field'}),
            "title": TextInput(attrs={'placeholder': 'Title of field'}),
            "description": Textarea(attrs={'placeholder': 'Description of the contents of the field'}),
        }


class DataSchemaConstraintForm(ModelForm):

    class Meta:
        model = DataSchemaConstraints
        fields = '__all__'
