from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from setsearch.models import Artist


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def artist(request: HttpRequest, slug: str) -> HttpResponse:
    # todo: handle 404
    artist = Artist.objects.get(slug=slug)
    return render(HttpRequest(), "artist.html", {"artist": artist})
