from http import HTTPStatus

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from setsearch.decorators import api
from setsearch.forms.api import *
from setsearch.models import Concert, Attendance, SetlistEntry, Comment, Artist


@require_POST
@api(ApiConcertAttendForm)
def api_concert_attend(request: HttpRequest, data: ApiConcertAttendForm) -> HttpResponse:
    with transaction.atomic():
        query = { "user": request.user, "concert": data["concert"] }
        qs = Attendance.objects.filter(**query)

        if qs.exists():
            qs.delete()
            attending = False
        else:
            Attendance.objects.create(**query)
            attending = True

    return JsonResponse({"attending": attending}, status=HTTPStatus.OK)

@require_POST
@api(ApiConcertRateForm)
def api_concert_rate(request: HttpRequest, data: ApiConcertRateForm) -> HttpResponse:
    """Updates the user's rating for a concert if they are attending it."""
    updated = Attendance.objects.filter(user=request.user, concert=data["concert"]).update(rating=data["rating"])
    if not updated:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    return HttpResponse(status=HTTPStatus.OK)

@require_POST
@api(ApiConcertUpdateForm)
def api_concert_update(request: HttpRequest, data: ApiConcertUpdateForm) -> HttpResponse:
    """Updates a concert's details and setlist."""
    concert: Concert = data["concert"]
    venue: Venue = data["venue"]

    # if the concert was last modified by the artist, only the artist and admins can edit it
    is_artist = request.user == concert.artist.user
    is_admin = request.user.is_superuser
    can_edit = is_admin or is_artist

    if concert.verified and not can_edit:
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    with transaction.atomic():
        # update concert fields
        concert.name = data["name"]
        concert.venue = venue
        concert.date = data["date"]
        concert.modified_by = request.user

        if not concert.verified and request.user == concert.artist.user:
            concert.verified = True

        concert.save()

        # update setlist efficiently
        SetlistEntry.objects.filter(concert=concert).delete()
        if data["setlist"]:
            SetlistEntry.objects.bulk_create(data["setlist"])

    return HttpResponse(status=HTTPStatus.OK)

@require_POST
@api(ApiConcertDeleteForm)
def api_concert_delete(request: HttpRequest, data: ApiConcertDeleteForm) -> HttpResponse:
    """Deletes a concert."""
    if not request.user.is_superuser and request.user != data["concert"].artist.user:
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    data["concert"].delete()
    return HttpResponse(status=HTTPStatus.OK)

@require_POST
@api(ApiArtistLinkForm)
def api_artist_link(request: HttpRequest, data: ApiArtistLinkForm) -> HttpResponse:
    """Links an artist to the user's accoun."""
    # admin only
    if not request.user.is_superuser:
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    # save link
    data["artist"].user = data["user"]
    data["artist"].save()

    return HttpResponse(status=HTTPStatus.OK)

# supports DELETE, so we can't use the @api decorator
def api_comment(request: HttpRequest) -> HttpResponse:
    """Handles creating and deleting comments on concerts."""
    if not request.user.is_authenticated:
        return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

    match request.method:
        case "POST":
            # create comment
            content = request.POST.get("content")
            concert = get_object_or_404(Concert, id=request.POST.get("concert"))
            Comment.objects.create(user=request.user, concert=concert, content=content)
        case "DELETE":
            # payload is sent as raw JSON
            data = orjson.loads(request.body)
            comment = Comment.objects.get(id=data.get("id"))

            # only the comment author and admins can delete this comment
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

def api_artist_list(_: HttpRequest) -> HttpResponse:
    """Returns a list of artists in the database."""
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)

