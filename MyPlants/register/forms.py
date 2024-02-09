from django import forms
from django.contrib.auth import login, authenticate 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    #save the info into user database
    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]
