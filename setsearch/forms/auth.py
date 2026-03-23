from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, CharField, PasswordInput

from setsearch.models import User


class SignUpForm(ModelForm):
    username = CharField()
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


class LoginForm(Form):
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


class ProfileForm(ModelForm):
    username = CharField()
    password = CharField(widget=PasswordInput(), required=False)
    password_confirm = CharField(widget=PasswordInput(), required=False, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password or password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("username", "email", "password")
