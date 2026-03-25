import orjson
from django.core.exceptions import ValidationError
from django.forms import Form
from django.forms.fields import IntegerField, CharField, DateField
from django.forms.models import ModelChoiceField

from setsearch.models import Concert, Venue, Song, SetlistEntry, Artist, User


class ApiConcertAttendForm(Form):
    concert = ModelChoiceField(queryset=Concert.objects.all())


class ApiConcertRateForm(Form):
    concert = ModelChoiceField(queryset=Concert.objects.all())
    rating = IntegerField(min_value=1, max_value=5)


class ApiConcertUpdateForm(Form):
    concert = ModelChoiceField(queryset=Concert.objects.all())
    name = CharField()
    venue = ModelChoiceField(queryset=Venue.objects.all())
    date = DateField()
    setlist = CharField()

    def clean_setlist(self):
        raw = self.cleaned_data.get("setlist", "[]")

        # parse json list
        try:
            data = orjson.loads(raw)
        except orjson.JSONDecodeError:
            raise ValidationError("Invalid JSON")

        if not isinstance(data, list):
            raise ValidationError("Expected a list")

        # parse songs
        songs = []
        concert = self.cleaned_data.get("concert")

        for v in data:
            if isinstance(v, int):
                try:
                    songs.append(Song.objects.get(id=v))
                except Song.DoesNotExist:
                    pass
            elif isinstance(v, str):
                song, _ = Song.objects.get_or_create(
                    title=v,
                    artist=concert.artist
                )
                songs.append(song)

        return [
            SetlistEntry(song=song, concert=concert, position=i) for i, song in enumerate(songs)
        ]


class ApiConcertDeleteForm(Form):
    concert = ModelChoiceField(queryset=Concert.objects.all())


class ApiArtistLinkForm(Form):
    artist = ModelChoiceField(queryset=Artist.objects.all())
    user = ModelChoiceField(queryset=User.objects.all(), required=False)
