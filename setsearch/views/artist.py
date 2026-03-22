from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from setsearch.forms.artist import LinkToUserForm
from setsearch.models import Artist, Concert, User


def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)
    concerts = Concert.objects.filter(artist=artist).order_by("-year", "-month", "-day")
    form = LinkToUserForm(artist)

    return render(request, "artist.html", {"artist": artist, "concerts": concerts, "form": form})

@require_POST
def link_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    elif not request.user.is_superuser:
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    # find user and artist
    artist = get_object_or_404(Artist, slug=artist_slug)
    username = request.POST.get("username")

    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = None

    # save link
    artist.user = user
    artist.save()

    return HttpResponse(status=HTTPStatus.OK)
