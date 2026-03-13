from django.http import HttpRequest, HttpResponse, JsonResponse

from setsearch.models import Artist


def list_artists(_: HttpRequest) -> HttpResponse:
    """Returns a list of artists (and their slugs) in the database."""
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)