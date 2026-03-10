from typing import TypeVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, OneToOneField, SET_NULL, ForeignKey, CASCADE, DateField, FloatField, \
    SmallIntegerField, DateTimeField, URLField, Index
from django.db.models.fields import SlugField
from django.utils import timezone
from django.utils.text import slugify

M = TypeVar("M", bound=Model)

def unique_slug(instance: M, field: str, value: str) -> str:
    slug = slugify(value)
    unique = slug
    n = 1
    Model = instance.__class__

    # increment n until slug is unique for field in model
    while Model.objects.filter(**{field: unique}).exists():
        unique = f"{slug}-{n}"
        n += 1

    return unique

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
        picture: WikiMedia artist picture filename. Prepend: https://commons.wikimedia.org/wiki/Special:FilePath/
    """

    mbid = CharField("MusicBrainz ID", max_length=36, primary_key=True)
    name = CharField(max_length=255, db_index=True)
    slug = SlugField(blank=True)
    user = OneToOneField(User, on_delete=SET_NULL, null=True, blank=True)  # 1-1
    picture = CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "slug", self.name)
        super().save(*args, **kwargs)

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

    def __str__(self):
        return f"{self.artist.name} @ {self.venue} [{self.date}]"


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

class Song(Model):
    """
    Attributes:
        mbid: The song's MusicBrainz ID.
        title: The song's title.
        artist: The artist who performed the song.
        picture: Cover art for the song.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, primary_key=True)
    title = CharField(max_length=255, db_index=True)
    artist = ForeignKey(Artist, on_delete=CASCADE) # 1-N
    picture = URLField(null=True, blank=True)


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

class Comment(Model):
    """A user commented on a concert."""

    user = ForeignKey(User, on_delete=CASCADE)
    concert = ForeignKey(Concert, on_delete=CASCADE)
    content = CharField(max_length=1000)
    timestamp = DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

        indexes = [
            Index(fields=["concert", "timestamp"]), # get comments for concert, ordered by timestamp
        ]