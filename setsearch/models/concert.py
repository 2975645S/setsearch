from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Model, ForeignKey, CASCADE, SET_NULL
from django.db.models.fields import CharField, SlugField, SmallIntegerField, DateTimeField
from django.utils import timezone

from setsearch.models.artist import Artist
from setsearch.models.util import unique_slug
from setsearch.models.venue import Venue


class Concert(Model):
    """
    Attributes:
        mbid: The concert's MusicBrainz ID.
        artist: The artist who performed the concert.
        name: The concert's title.
        slug: A URL-friendly version of the concert's title.
        year: The year the concert took place.
        month: The month the concert took place.
        day: The day the concert took place.
        venue: The venue that the concert was performed in.
        last_modified: The date the concert was last modified.
        modified_by: The SetSearch user who most recently modified the concert.
    """

    mbid = CharField("MusicBrainz ID", max_length=36, unique=True, null=True, blank=True)
    artist = ForeignKey(Artist, on_delete=CASCADE, db_index=True)  # 1-N
    name = CharField(max_length=255, blank=True)
    slug = SlugField(blank=True)
    year = SmallIntegerField()
    month = SmallIntegerField(null=True)
    day = SmallIntegerField(null=True)
    venue = ForeignKey(Venue, on_delete=CASCADE, null=True)
    last_modified = DateTimeField(default=timezone.now)
    modified_by = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.name:
            parts = [self.artist.name]

            if self.venue and self.venue.name:
                parts.append(f"at {self.venue.name}")

            # build date string if at least year exists
            date_parts = []
            if self.day:
                date_parts.append(f"{self.day:02}")  # zero-padded
            if self.month:
                date_parts.append(f"{self.month:02}")  # zero-padded
            if self.year:
                date_parts.append(str(self.year))

            if date_parts:
                parts.append("on " + "-".join(date_parts))

            self.name = " ".join(parts)

        if not self.slug:
            self.slug = unique_slug(self, "slug", self.name)

        super().save(*args, **kwargs)

    def date(self) -> date:
        return date(self.year, self.month, self.day)

    def clean(self):
        if self.day and not self.month:
            raise ValidationError("Month must be provided if day is provided.")
        if self.month and not (1 <= self.month <= 12):
            raise ValidationError("Month must be between 1 and 12.")
        if self.day and not (1 <= self.day <= 31):
            raise ValidationError("Day must be between 1 and 31.")

    def __str__(self):
        return self.name