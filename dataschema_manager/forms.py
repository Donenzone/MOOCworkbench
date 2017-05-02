from django.forms import ModelForm
from django.forms import TextInput, Textarea

from .models import DataSchemaField


class DataSchemaFieldForm(ModelForm):
    class Meta:
        model = DataSchemaField
        fields = '__all__'

        widgets = {
            "name": TextInput(attrs={'placeholder': 'Name of field'}),
            "title": TextInput(attrs={'placeholder': 'Title of field'}),
            "description": Textarea(attrs={'placeholder': 'Description of the contents of the field'}),
            "format": TextInput(attrs={'placeholder': '(optional) Define a format (only for Date/Time/DateTime)'}),
            "minimum": TextInput(attrs={'placeholder': '(optional) Define a minimum value (only for Number/Date/Time/DateTime)'}),
            "maximum": TextInput(attrs={'placeholder': '(optional) Define a maximum value (only for Number/Date/Time/DateTime)'}),
        }
