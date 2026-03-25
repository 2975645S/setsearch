from django.forms import Form, DateField, DateInput
from django.forms.models import ModelForm
from django_select2.forms import ModelSelect2Widget

from setsearch.forms import CreateModelField, ArtistSongField
from setsearch.models import Concert, Artist, Venue, Song


class CreateConcertForm(ModelForm):
    artist = CreateModelField(Artist, required=True)
    venue = CreateModelField(Venue, required=True)
    date = DateField(widget=DateInput(attrs={"type": "date"}), required=True)

    def save(self, commit=True):
        concert = super().save(commit=False)
        date = self.cleaned_data["date"]
        concert.set_date(date.year, date.month, date.day)
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

    def save(self, commit=True):
        concert = super().save(commit=False)
        concert.set_date(self.cleaned_data["date"])
        if commit:
            concert.save()
        return concert

    class Meta:
        model = Concert
        fields = ("name", "venue")


class SetlistWidget(ModelSelect2Widget):
    model = Song
    search_fields = ["title__icontains"]

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.update({
            "data-placeholder": "Search for a song...",
            "data-minimum-input-length": "0",
        })
        return attrs

    def label_from_instance(self, song: Song):
        return song.title


class SetlistForm(Form):
    def __init__(self, artist: Artist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["song"] = ArtistSongField(artist)
