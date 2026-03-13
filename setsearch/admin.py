from django.contrib.admin import ModelAdmin, register, display
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from setsearch.models import *


# proxy the custom user into the auth app category
class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "auth"

# remove first_name and last_name
@register(AdminUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

@register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ("name", "mbid")

@register(Concert)
class ConcertAdmin(ModelAdmin):
    list_display = ("title", "artist", "date")

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
    ...

@register(Song)
class SongAdmin(ModelAdmin):
    list_display = ("title", "artist", "mbid")

@register(SetlistEntry)
class SetlistEntryAdmin(ModelAdmin):
    ...

@register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("concert", "user", "timestamp", "content")