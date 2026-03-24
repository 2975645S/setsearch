from django.db.models.aggregates import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from setsearch.forms.artist import ArtistLinkForm
from setsearch.models import Artist, Concert, Song, Attendance

SONG_COUNT = 5


@require_GET
def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    """Artist page displaying the artist's details and a list of their concerts."""
    artist = get_object_or_404(Artist, slug=artist_slug)
    concerts = Concert.objects.filter(artist=artist).order_by("-date")
    songs = Song.objects.filter(artist=artist).annotate(play_count=Count("setlistentry")).filter(
        play_count__gt=0).order_by("-play_count")[:SONG_COUNT]
    attendee_count = Attendance.objects.filter(concert__artist=artist).count()
    form = ArtistLinkForm(artist)

    return render(request, "artist.html",
                  {"artist": artist, "concerts": concerts, "songs": songs, "attendee_count": attendee_count,
                   "form": form})
