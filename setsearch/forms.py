from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms.fields import CharField, EmailField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput, TextInput, NumberInput, Select

from setsearch.models import Comment, Concert
from setsearch.models import User


class SignUpForm(ModelForm):
    username = CharField()
    email = EmailField()
    password = CharField(widget=PasswordInput())

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("username", "email", "password")


class LoginForm(forms.Form):
    username = CharField()
    password = CharField(widget=PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Invalid username or password.")
            cleaned_data["user"] = user

        return cleaned_data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Leave a comment..."})
        }


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = ["title", "venue", "year", "month", "day"]
        widgets = {
            "title": TextInput(attrs={"class": "input input-bordered w-full"}),
            "year": NumberInput(attrs={"class": "input input-bordered w-full"}),
            "month": NumberInput(attrs={"class": "input input-bordered w-full"}),
            "day": NumberInput(attrs={"class": "input input-bordered w-full"}),
            "venue": Select(attrs={"id": "venue-select"})
        }
