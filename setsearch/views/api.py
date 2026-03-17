from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from setsearch.forms.concert import CommentForm
from setsearch.models import Artist, Comment
from setsearch.models import Concert


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


@login_required
@require_POST
def create_comment(request, concert_id: str) -> JsonResponse:
    """
    Creates a comment for the given concert and returns the comment data as JSON.
    """
    concert = get_object_or_404(Concert, mbid=concert_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.concert = concert
        comment.save()
        return JsonResponse({
            "username": request.user.username,
            "content": comment.content,
            "timestamp": comment.timestamp.strftime("%d %b %Y %H:%M"),
        })
    return JsonResponse({"error": "Invalid form"}, status=400)
