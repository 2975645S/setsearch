from django.db.models import Model
from django.db.models.fields import CharField


class Venue(Model):
    """
    Attributes:
        mbid: The venue's MusicBrainz ID.
        name: The venue's name.
        city: The city the venue is located in.
        address: The venue's address.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, unique=True, null=True, blank=True)
    name = CharField(max_length=255)
    city = CharField(max_length=255, null=True)
    address = CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.name}, {self.city}"
