from userauth.models import Profile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class EditProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}), required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}), required=True
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}), required=True
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}), required=True
    )

    class Meta:
        model = Profile
        fields = ["picture", "first_name", "last_name", "location", "bio"]


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(),
        max_length=50,
        required=True,
    )

    email = forms.EmailField(widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
