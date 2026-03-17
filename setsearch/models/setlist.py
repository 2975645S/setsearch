from django.db.models import Model, ForeignKey, Index, CASCADE
from django.db.models.fields import SmallIntegerField

from setsearch.models.concert import Concert
from setsearch.models.song import Song


class SetlistEntry(Model):
    """
    A song was performed during a concert.

    Attributes:
        song: The song in the setlist.
        concert: The concert the song was performed at.
        position: The position of the song in the setlist.
    """

    song = ForeignKey(Song, on_delete=CASCADE)
    concert = ForeignKey(Concert, on_delete=CASCADE)
    position = SmallIntegerField()

    class Meta:
        verbose_name = "setlist entry"
        verbose_name_plural = "setlist entries"

        indexes = [
            Index(fields=["concert", "position"]),  # get setlist for concert, ordered by position
        ]
