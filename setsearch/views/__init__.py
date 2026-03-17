from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from setsearch.models import Artist, Concert


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")

def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)
    concerts = Concert.objects.filter(artist=artist).order_by("-year", "-month", "-day")
    return render(request, "artist.html", {"artist": artist, "concerts": concerts})
