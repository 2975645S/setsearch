from django.contrib.admin import register, display
from unfold.admin import ModelAdmin

from setsearch.models import *


@register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ("name", "mbid")

@register(Venue)
class Venue(ModelAdmin):
    list_display = ("name", "city")

@register(Concert)
class ConcertAdmin(ModelAdmin):
    list_display = ("name", "artist", "venue", "date")

    @display
    def date(self, obj):
        parts = [str(obj.year)]

        if obj.month:
            parts.insert(0, f"{obj.month:02}")
        if obj.day:
            parts.insert(0, f"{obj.day:02}")

        return "-".join(parts)


@register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ("user", "concert")

@register(Song)
class SongAdmin(ModelAdmin):
    list_display = ("title", "artist", "mbid")

@register(SetlistEntry)
class SetlistEntryAdmin(ModelAdmin):
    list_display = ("song", "concert", "position")

@register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("concert", "user", "timestamp", "content")