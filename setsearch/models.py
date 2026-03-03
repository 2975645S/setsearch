from django.contrib.auth.models import User
from django.db.models import CharField, Model, OneToOneField, SET_NULL, ForeignKey, CASCADE, DateField, FloatField, \
    ManyToManyField, SmallIntegerField, DateTimeField
from django.utils import timezone


class Artist(Model):
    """
    Attributes:
        mbid: The artist's MusicBrainz ID.
        name: The artist's stage name.
        user: The artist's SetSearch account.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, primary_key=True)
    name = CharField(max_length=255)
    user = OneToOneField(User, on_delete=SET_NULL, null=True, blank=True)  # 1-1


class Concert(Model):
    """
    Attributes:
        artist: The artist who performed the concert.
        date: The date the concert was performed.
        venue: The venue who performed the concert.
        last_modified: The date the concert was last modified.
        modified_by: The SetSearch user who most recently modified the concert.
    """

    artist = ForeignKey(Artist, on_delete=CASCADE)  # 1-N
    date = DateField()
    venue = CharField(max_length=255)
    last_modified = DateTimeField(default=timezone.now)
    modified_by = OneToOneField(User, on_delete=SET_NULL, null=True)


class Attendance(Model):
    """
    A user has attended a concert.

    Attributes:
        user: The user who attended the concert.
        concert: The concert that was attended.
        rating: The user's rating of the concert on a 5-star scale.
    """

    user = ForeignKey(User, on_delete=CASCADE)
    concert = ForeignKey(Concert, on_delete=CASCADE)
    rating = FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Concert Attendance"
        verbose_name_plural = "Concert Attendances"


class Genre(Model):
    """
    Attributes:
        name: The genre's name.
    """

    name = CharField(max_length=255)


class Song(Model):
    """
    Attributes:
        mbid: The song's MusicBrainz ID.
        name: The song's name.
        genres: The genres associated with the song.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, primary_key=True)
    name = CharField(max_length=255)
    genres = ManyToManyField(Genre, blank=True)  # N-M


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
        verbose_name = "Setlist Entry"
        verbose_name_plural = "Setlist Entries"
