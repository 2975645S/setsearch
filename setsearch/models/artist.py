from django.contrib.auth import get_user_model
from django.db.models import Model, OneToOneField, SET_NULL
from django.db.models.fields import CharField, SlugField

from setsearch.models.util import unique_slug


class Artist(Model):
    """
    Attributes:
        mbid: The artist's MusicBrainz ID.
        name: The artist's stage name.
        slug: A URL-friendly version of the artist's name.
        user: The artist's SetSearch account.
        picture: WikiMedia artist picture filename. Prepend: https://commons.wikimedia.org/wiki/Special:FilePath/
    """

    mbid = CharField("MusicBrainz ID", max_length=36, unique=True, null=True, blank=True)
    name = CharField(max_length=255, db_index=True)
    slug = SlugField(blank=True)
    user = OneToOneField(get_user_model(), on_delete=SET_NULL, null=True, blank=True)  # 1-1
    picture = CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, "slug", self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name