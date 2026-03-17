from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import CharField, URLField

from setsearch.models.artist import Artist


class Song(Model):
    """
    Attributes:
        mbid: The song's MusicBrainz ID.
        title: The song's title.
        artist: The artist who performed the song.
        picture: Cover art for the song.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, unique=True, blank=True)
    title = CharField(max_length=255, db_index=True)
    artist = ForeignKey(Artist, on_delete=CASCADE)  # 1-N
    picture = URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.artist.name} - {self.title}"
