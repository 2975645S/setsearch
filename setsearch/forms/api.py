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

        try:
            data = orjson.loads(raw)
        except orjson.JSONDecodeError:
            raise ValidationError("Invalid JSON")

        if not isinstance(data, list):
            raise ValidationError("Expected a list")

        try:
            ids = [int(x) for x in data]
        except (TypeError, ValueError):
            raise ValidationError("All items must be integers")

        songs = Song.objects.filter(id__in=ids)
        song_map = {s.id: s for s in songs}

        # validate all ids exist
        missing = [i for i in ids if i not in song_map]
        if missing:
            raise ValidationError(f"Invalid song IDs: {missing}")

        # preserve order
        ordered_songs = [song_map[i] for i in ids]

        return [
            SetlistEntry(
                song=song,
                concert=self.cleaned_data["concert"],
                position=i
            )
            for i, song in enumerate(ordered_songs)
        ]

class ApiArtistLinkForm(Form):
    artist = ModelChoiceField(queryset=Artist.objects.all())
    user = ModelChoiceField(queryset=User.objects.all(), required=False)