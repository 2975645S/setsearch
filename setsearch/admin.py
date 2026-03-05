from django.contrib.admin import ModelAdmin, register

from setsearch.models import *


@register(Artist)
class ArtistAdmin(ModelAdmin):
    list_dispay = ("name", "mbid")


@register(Concert)
class ConcertAdmin(ModelAdmin):
    ...


@register(Attendance)
class AttendanceAdmin(ModelAdmin):
    ...


@register(Genre)
class GenreAdmin(ModelAdmin):
    ...


@register(Song)
class SongAdmin(ModelAdmin):
    ...


@register(SetlistEntry)
class SetlistEntryAdmin(ModelAdmin):
    ...
