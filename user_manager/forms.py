from django import forms
from django.contrib.auth.models import User

from .models import User, WorkbenchUser


class UserLoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class WorkbenchUserForm(forms.ModelForm):
    netid = forms.CharField(required=True, label="TU Delft Net ID")
    current_password = forms.CharField(widget=forms.PasswordInput(),
                                       help_text="Leave empty if you do not wish to change your password",
                                       required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password_again = forms.CharField(widget=forms.PasswordInput(), required=False, label="Password (confirmation)")

    class Meta:
        model = WorkbenchUser
        fields = ('netid', 'current_password', 'new_password', 'new_password_again')


class RegisterForm(forms.ModelForm):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    password_again = forms.CharField(required=True, widget=forms.PasswordInput(), label="Password (confirmation)")
    netid = forms.CharField(required=True, label="TU Delft Net ID")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_again', 'netid')
