from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from setsearch.forms.artist import ArtistLinkForm
from setsearch.models import Artist, Concert


def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)
    concerts = Concert.objects.filter(artist=artist).order_by("-year", "-month", "-day")
    form = ArtistLinkForm(artist)

    return render(request, "artist.html", {"artist": artist, "concerts": concerts, "form": form})
