from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from setsearch.forms import CommentForm, ConcertForm
from setsearch.models import Artist, Concert, Comment, SetlistEntry


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)
    concerts = Concert.objects.filter(artist=artist).order_by("-year", "-month", "-day")
    return render(request, "artist.html", {"artist": artist, "concerts": concerts})


def view_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    concert = get_object_or_404(Concert, slug=concert_slug, artist__slug=artist_slug)
    comments = Comment.objects.filter(concert=concert).order_by("timestamp")
    setlist = SetlistEntry.objects.filter(concert=concert).order_by("position")

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.user = request.user
            comment.concert = concert
            comment.save()

            # stop accidental resubmission on page refresh
            # by making a GET request
            return redirect("concert", artist_slug=artist_slug, concert_slug=concert_slug)
    else:
        form = CommentForm()

    return render(request, "concert.html", {"concert": concert, "comments": comments, "setlist": setlist, "form": form})


@login_required
def create_concert(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)

    if not (request.user.is_superuser or request.user == artist.user):
        return redirect("home")

    if request.method == "POST":
        form = ConcertForm(request.POST)
        if form.is_valid():
            concert = form.save(commit=False)
            concert.artist = artist
            concert.modified_by = request.user
            concert.save()
            return redirect("concert", artist_slug=artist_slug, concert_slug=concert.slug)
    else:
        form = ConcertForm()

    return render(request, "create_concert.html", {"form": form, "artist": artist})