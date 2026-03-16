from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms.fields import CharField, DateField
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput, DateInput
from django_select2.forms import ModelSelect2Widget

from setsearch.models import Comment, Concert, User, Artist, Venue


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


class ArtistWidget(ModelSelect2Widget):
    model = Artist
    search_fields = ['name__icontains']

class VenueWidget(ModelSelect2Widget):
    model = Venue
    search_fields = ["name__icontains", "city__icontains"]

class ConcertForm(ModelForm):
    date = DateField(required=True, widget=DateInput(attrs={"type": "date"}))

    class Meta:
        model = Concert
        fields = ("title", "artist", "venue")
        widgets = {
            "artist": ArtistWidget(),
            "venue": VenueWidget()
        }

    def save(self, commit = True):
        concert = super().save(commit=False)

        # add date
        date = self.cleaned_data.get("date")
        concert.year = date.year
        concert.month = date.month
        concert.day = date.day

        if commit:
            concert.save()

        return concert

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Leave a comment..."})
        }