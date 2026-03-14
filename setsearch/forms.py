from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from setsearch.models import User, Comment


class SignUpForm(ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "input w-full",
            "placeholder": "Username"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input w-full",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input w-full",
            "placeholder": "Password"
        })
    )

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
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "input w-full",
            "placeholder": "Username"
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "input w-full",
            "placeholder": "Password"
        })
    )

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
