import datetime

from django.core.exceptions import ValidationError
from django.db.models import Model, F, ForeignKey, CASCADE, SET_NULL, IntegerChoices
from django.db.models.fields import CharField, SlugField, DateField, DateTimeField, BooleanField, SmallIntegerField
from django.utils import timezone

from setsearch.models.artist import Artist
from setsearch.models.user import User
from setsearch.models.util import unique_slug
from setsearch.models.venue import Venue


class Concert(Model):
    """
    Attributes:
        mbid: The concert's MusicBrainz ID.
        artist: The artist who performed the concert.
        name: The concert's title.
        slug: A URL-friendly version of the concert's title.
        date: The date the concert was performed, with varying precision.
        precision: The precision of the date field (year, month, day, or none).
        venue: The venue that the concert was performed in.
        last_modified: The date the concert was last modified.
        modified_by: The SetSearch user who most recently modified the concert.
    """

    class DatePrecision(IntegerChoices):
        NONE = 0, "None"
        YEAR = 1, "Year"
        MONTH = 2, "Month"
        DAY = 3, "Day"

    mbid = CharField("MusicBrainz ID", max_length=36, unique=True, null=True, blank=True)
    artist = ForeignKey(Artist, on_delete=CASCADE, db_index=True)  # 1-N
    name = CharField(max_length=255, blank=True)
    slug = SlugField(blank=True)
    venue = ForeignKey(Venue, on_delete=CASCADE, null=True)
    last_modified = DateTimeField(default=timezone.now)
    modified_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    verified = BooleanField(default=False)

    date = DateField(null=True, blank=True)  # canonical, always
    precision = SmallIntegerField(choices=DatePrecision.choices, default=DatePrecision.NONE)

    def save(self, *args, **kwargs):
        if not self.name:
            parts = [self.artist.name]

            if self.venue and self.venue.name:
                parts.append(f"at {self.venue.name}")

            if self.date:
                parts.append(f"on {self.date_str()}")

            self.name = " ".join(parts)

        if not self.slug:
            self.slug = unique_slug(self, "slug", self.name)

        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        if self.precision == self.DatePrecision.NONE and self.date is not None:
            raise ValidationError("Date must be null when precision is NONE.")
        if self.precision != self.DatePrecision.NONE and self.date is None:
            raise ValidationError("Date is required unless precision is NONE.")

    def set_date(self, year: int | None = None, month: int | None = None, day: int | None = None):
        if year is None:
            self.date = None
            self.precision = self.DatePrecision.NONE
        elif month is None:
            self.date = datetime.date(year, 1, 1)
            self.precision = self.DatePrecision.YEAR
        elif day is None:
            self.date = datetime.date(year, month, 1)
            self.precision = self.DatePrecision.MONTH
        else:
            self.date = datetime.date(year, month, day)
            self.precision = self.DatePrecision.DAY

    def date_str(self) -> str:
        if not self.date:
            return "Unknown date"

        if self.precision == self.DatePrecision.YEAR:
            return self.date.strftime("??-??-%Y")
        elif self.precision == self.DatePrecision.MONTH:
            return self.date.strftime("??-%m-%Y")
        else:
            return self.date.strftime("%d-%m-%Y")

    @property
    def year(self) -> int | None:
        return self.date.year if self.date else None

    def __str__(self):
        return self.name

    class Meta:
        ordering = [F("date").asc(nulls_last=True)]
