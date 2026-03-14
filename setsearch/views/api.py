from django.http import HttpRequest, HttpResponse, JsonResponse

from setsearch.models import Artist, Comment


def list_artists(_: HttpRequest) -> HttpResponse:
    """Returns a list of artists (and their slugs) in the database."""
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)

def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    comment = Comment.objects.get(id=comment_id)

    if not comment:
        return HttpResponse(status=404)

    if request.user == comment.user:
        comment.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)
