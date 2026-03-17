from django.forms import DateField, DateInput
from django.forms.models import ModelForm

from setsearch.forms import CreateModelField
from setsearch.models import Concert, Artist, Venue


class ConcertForm(ModelForm):
    artist = CreateModelField(Artist, required=True)
    venue = CreateModelField(Venue, required=True)
    date = DateField(widget=DateInput(attrs={"type": "date"}), required=True)


    def save(self, commit = True):
        concert = super().save(commit=False)

        # add the date
        date = self.cleaned_data["date"]
        concert.year = date.year
        concert.month = date.month
        concert.day = date.day

        # save if necessary
        if commit:
            concert.save()

        return concert

    class Meta:
        model = Concert
        fields = ("name", "artist", "venue")