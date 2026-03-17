from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from setsearch.forms.concert import ConcertForm
from setsearch.models import Concert, Comment, SetlistEntry


def view_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    concert = get_object_or_404(Concert, slug=concert_slug, artist__slug=artist_slug)
    comments = Comment.objects.filter(concert=concert).order_by("timestamp")
    setlist = SetlistEntry.objects.filter(concert=concert).order_by("position")

    return render(request, "concert.html", {"concert": concert, "comments": comments, "setlist": setlist})


@login_required
def create_concert(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ConcertForm(request.POST)
        if form.is_valid():
            concert = form.save(commit=False)
            concert.modified_by = request.user
            concert.save()
            return redirect("concert", artist_slug=concert.artist.slug, concert_slug=concert.slug)
    else:
        form = ConcertForm()

    return render(request, "create_concert.html", {"form": form})