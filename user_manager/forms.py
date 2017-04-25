from django import forms
from .models import User, WorkbenchUser
from django.contrib.auth.models import User


class UserLoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class WorkbenchUserForm(forms.ModelForm):
    netid = forms.CharField(required=True, label="TU Delft Net ID")

    class Meta:
        model = WorkbenchUser
        fields = ('netid',)


class RegisterForm(forms.ModelForm):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    password_again = forms.CharField(required=True, widget=forms.PasswordInput(), label="Password (confirmation)")
    netid = forms.CharField(required=True, label="TU Delft Net ID")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_again', 'netid')