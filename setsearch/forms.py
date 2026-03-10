from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import Form
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput

from setsearch.models import User


class SignUpForm(ModelForm):
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
    username = CharField(label="Username")
    password = CharField(label="Password", widget=PasswordInput())

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
