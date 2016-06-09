from django import forms
from .models import User, WorkbenchUser
from django.contrib.auth.models import User

class UserLoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class RegisterForm(forms.ModelForm):
    password_again = forms.CharField(required=True, widget=forms.PasswordInput())
    tu_net_id = forms.CharField(required=True, label="TU Delft Net ID")
    class Meta:
        model = User
        fields = ('username', 'email', 'password')