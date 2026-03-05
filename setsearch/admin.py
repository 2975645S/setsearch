from django.contrib.admin import ModelAdmin, register
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
    list_display = ("name", "picture")

@register(Concert)
class ConcertAdmin(ModelAdmin):
    ...


@register(Attendance)
class AttendanceAdmin(ModelAdmin):
    ...

@register(Genre)
class GenreAdmin(ModelAdmin):
    search_fields = ("name",)


@register(Song)
class SongAdmin(ModelAdmin):
    list_display = ("title", "artist", "genre_list")
    autocomplete_fields = ("genres",)

    def genre_list(self, obj):
        return ", ".join(g.name for g in obj.genres.all())
    genre_list.short_description = "Genres"

@register(SetlistEntry)
class SetlistEntryAdmin(ModelAdmin):
    ...
