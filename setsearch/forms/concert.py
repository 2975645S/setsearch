from django.forms import DateField, DateInput
from django.forms.models import ModelForm

from setsearch.forms import CreateModelField
from setsearch.models import Concert, Artist, Venue


class CreateConcertForm(ModelForm):
    artist = CreateModelField(Artist, required=True)
    venue = CreateModelField(Venue, required=True)
    date = DateField(widget=DateInput(attrs={"type": "date"}), required=True)


    def save(self, commit = True):
        concert = super().save(commit=False)
        concert.set_date(self.cleaned_data["date"])
        if commit:
            concert.save()
        return concert

    class Meta:
        model = Concert
        fields = ("name", "artist", "venue")

class EditConcertForm(ModelForm):
    venue = CreateModelField(Venue)
    date = DateField(widget=DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["venue"].initial = self.instance.venue
        self.fields["date"].initial = self.instance.date

    def save(self, commit = True):
        concert = super().save(commit=False)
        concert.set_date(self.cleaned_data["date"])
        if commit:
            concert.save()
        return concert

    class Meta:
        model = Concert
        fields = ("name", "venue")