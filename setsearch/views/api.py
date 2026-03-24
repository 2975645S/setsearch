from http import HTTPStatus

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
    # find concert and attendance
    attendance, attending = Attendance.objects.get_or_create(user=request.user, concert=data["concert"])

    # remove attendance if it already exists (toggle)
    if not attending:
        attendance.delete()

    return JsonResponse({"attending": attending})

@require_POST
@api(ApiConcertRateForm)
def api_concert_rate(request: HttpRequest, data: ApiConcertRateForm) -> HttpResponse:
    # find attendance
    attendance = get_object_or_404(Attendance, user=request.user, concert=data["concert"])

    # update rating
    attendance.rating = data["rating"]
    attendance.save()

    return HttpResponse(status=HTTPStatus.OK)

@require_POST
@api(ApiConcertUpdateForm)
def api_concert_update(request: HttpRequest, data: ApiConcertUpdateForm) -> HttpResponse:
    concert: Concert = data["concert"]
    venue: Venue = data["venue"]

    # if the concert was last modified by the artist, only the artist and superusers can edit it
    if concert.verified and not (request.user.is_superuser or request.user == concert.artist.user):
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    # update the concert
    concert.name = data["name"]
    concert.venue = venue
    concert.set_date(data["date"])
    concert.modified_by = request.user

    if not concert.verified and request.user == concert.artist.user:
        concert.verified = True

    concert.save()

    # update setlist
    existing = SetlistEntry.objects.filter(concert=concert)
    existing.delete()
    SetlistEntry.objects.bulk_create(data["setlist"])

    return HttpResponse(status=HTTPStatus.OK)

# todo: fix client side
@require_POST
@api(ApiArtistLinkForm)
def api_artist_link(request: HttpRequest, data: ApiArtistLinkForm) -> HttpResponse:
    # admin only
    if not request.user.is_superuser:
        return HttpResponse(status=HTTPStatus.FORBIDDEN)

    # save link
    data["artist"].user = data["user"]
    data["artist"].save()

    return HttpResponse(status=HTTPStatus.OK)

    # if not request.user.is_authenticated:
    #     return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    # elif not request.user.is_superuser:
    #     return HttpResponse(status=HTTPStatus.FORBIDDEN)
    #
    # # find user and artist
    # artist = get_object_or_404(Artist, slug=artist_slug)
    # username = request.POST.get("username")
    #
    # if username:
    #     user = get_object_or_404(User, username=username)
    # else:
    #     user = None
    #
    # # save link
    # artist.user = user
    # artist.save()
    #
    # return HttpResponse(status=HTTPStatus.OK)


# supports DELETE, so we can't use the @api decorator
def api_comment(request: HttpRequest) -> HttpResponse:
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

def api_artist_list(_: HttpRequest) -> HttpResponse:
    """Returns a list of artists (and their slugs) in the database."""
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)

