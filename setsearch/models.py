from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, OneToOneField, SET_NULL, ForeignKey, CASCADE, DateField, FloatField, \
    ManyToManyField, SmallIntegerField, DateTimeField, URLField, Index
from django.utils import timezone

class User(AbstractUser):
    first_name = None
    last_name = None

    def __str__(self):
        return self.username

class Artist(Model):
    """
    Attributes:
        mbid: The artist's MusicBrainz ID.
        name: The artist's stage name.
        user: The artist's SetSearch account.
        picture: A URL to a picture of the artist.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, primary_key=True)
    name = CharField(max_length=255, db_index=True)
    user = OneToOneField(User, on_delete=SET_NULL, null=True, blank=True)  # 1-1
    picture = URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class Concert(Model):
    """
    Attributes:
        artist: The artist who performed the concert.
        date: The date the concert was performed.
        venue: The venue who performed the concert.
        last_modified: The date the concert was last modified.
        modified_by: The SetSearch user who most recently modified the concert.
    """

    artist = ForeignKey(Artist, on_delete=CASCADE, db_index=True)  # 1-N
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
        verbose_name = "attendance"
        verbose_name_plural = "attendances"

        indexes = [
            Index(fields=["user", "concert"]) # has user attended concert?
        ]


class Genre(Model):
    """
    Attributes:
        name: The genre's name.
    """

    name = CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name


class Song(Model):
    """
    Attributes:
        track_mbid: The song's MusicBrainz Track ID.
        release_mbid: The song's MusicBrainz Release ID.
        title: The song's title.
        artist: The artist who performed the song.
        genres: The genres associated with the song.
    """

    track_mbid = CharField("MusicBrainz Track ID", max_length=36, primary_key=True)
    release_mbid = CharField("MusicBrainz Release ID", max_length=36, null=True, blank=True)
    title = CharField(max_length=255, db_index=True)
    artist = ForeignKey(Artist, on_delete=CASCADE) # 1-N
    genres = ManyToManyField(Genre, blank=True)    # N-M

    def __str__(self):
        return f"{self.artist.name} - {self.title}"


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
            Index(fields=["concert", "position"]), # get setlist for concert, ordered by position
        ]