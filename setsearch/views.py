from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from setsearch.models import Artist


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def artist(request: HttpRequest, artist_id: str) -> HttpResponse:
    artist = Artist.objects.get(mbid=artist_id)
    return render(HttpRequest(), "artist.html", {"artist": artist})
