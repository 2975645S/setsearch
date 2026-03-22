from http import HTTPStatus

import orjson
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from setsearch.models import Artist, Concert, Comment, Attendance


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
