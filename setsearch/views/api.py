from datetime import datetime
from http import HTTPStatus

import orjson
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from setsearch.models import Artist, Concert, Comment, Attendance, SetlistEntry, Venue, Song


def list_artists(_: HttpRequest) -> HttpResponse:
    """Returns a list of artists (and their slugs) in the database."""
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)


def comment(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

    match request.method:
        case "POST":
            # create comment
            content = request.POST.get("content")
            concert = get_object_or_404(Concert, id=request.POST.get("concert"))
            Comment.objects.create(user=request.user, concert=concert, content=content)
        case "DELETE":
            data = orjson.loads(request.body)
            comment = Comment.objects.get(id=data.get("id"))

            if request.user != comment.user and not request.user.is_superuser:
                return HttpResponse(status=HTTPStatus.FORBIDDEN)

            concert = comment.concert
            comment.delete()
        case _:
            return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)

    # render comments
    comments = Comment.objects.filter(concert_id=concert.id).select_related("user")
    html = render_to_string("partials/comments.html", {"comments": comments, "request": request})
    return JsonResponse({"html": html})


@require_POST
def attend(request: HttpRequest, concert_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

    concert = get_object_or_404(Concert, id=concert_id)
    attendance, created = Attendance.objects.get_or_create(user=request.user, concert=concert)

    if not created:
        attendance.delete()

    return JsonResponse({"attending": created})


@require_POST
def rating(request: HttpRequest, concert_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

    # find attendance
    concert = get_object_or_404(Concert, id=concert_id)
    attendance = get_object_or_404(Attendance, user=request.user, concert=concert)

    # update rating
    rating = int(request.POST.get("rating"))
    attendance.rating = rating
    attendance.save()

    return HttpResponse(status=HTTPStatus.OK)


@require_POST
def update_concert(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

    # find the concert
    concert_id = request.POST.get("concert_id")
    concert = get_object_or_404(Concert, id=concert_id)

    # if the concert was last modified by the artist, only the artist and superusers can edit it
    if concert.verified and not (request.user.is_superuser or request.user == concert.artist.user):
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    # update the concert
    name = request.POST.get("name", concert.name)
    venue: Venue = request.POST.get("venue_id", concert.venue)

    if type(venue) == str:
        venue = get_object_or_404(Venue, id=venue)

    date = request.POST.get("date", concert.date)

    concert.name = name
    concert.venue = venue
    concert.set_date(datetime.strptime(date, "%Y-%m-%d").date())
    concert.modified_by = request.user

    if not concert.verified and request.user == concert.artist.user:
        concert.verified = True

    concert.save()

    # update setlist
    existing = SetlistEntry.objects.filter(concert=concert)
    existing.delete()

    setlist = orjson.loads(request.POST.get("setlist", "[]"))
    songs = Song.objects.filter(id__in=setlist)
    song_map = {song.id: song for song in songs}
    new = [
        SetlistEntry(
            song=song_map[song_id],
            concert=concert,
            position=i
        )
        for i, song_id in enumerate(setlist)
        if song_id in song_map
    ]

    SetlistEntry.objects.bulk_create(new)

    return HttpResponse(status=HTTPStatus.OK)
