from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from setsearch.models import Artist


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def artist(request: HttpRequest, slug: str) -> HttpResponse:
    # todo: handle 404
    artist = Artist.objects.get(slug=slug)
    return render(HttpRequest(), "artist.html", {"artist": artist})


def artist_list(request: HttpRequest) -> HttpResponse:
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)
# def search(request: HttpRequest) -> HttpResponse:
#     """Search for artists by name using fuzzy matching."""
#
#     query = request.GET.get("query", "")
#     artists = list(Artist.objects.values_list("name", flat=True))
#     print(artists)
#     matches = process.extract(query, artists, limit=10, scorer=fuzz.partial_ratio, score_cutoff=10)
#
#     results = [{"name": matches[0], "score": matches[1]} for matches in matches]
#     return JsonResponse({"results": results})
