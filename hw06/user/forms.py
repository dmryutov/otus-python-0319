from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    """
    User sign up form
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar')


class SettingsForm(forms.ModelForm):
    """
    User settings form
    """
    class Meta:
        model = User
        fields = ('email', 'avatar')
