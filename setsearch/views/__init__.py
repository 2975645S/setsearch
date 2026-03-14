from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from setsearch.forms import CommentForm
from setsearch.models import Artist, Concert, Comment, SetlistEntry


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def view_artist(request: HttpRequest, artist_slug: str) -> HttpResponse:
    artist = get_object_or_404(Artist, slug=artist_slug)
    return render(request, "artist.html", {"artist": artist})


def view_concert(request: HttpRequest, concert_id: str) -> HttpResponse:
    concert = get_object_or_404(Concert, mbid=concert_id)
    comments = Comment.objects.filter(concert=concert).order_by("timestamp")
    setlist = SetlistEntry.objects.filter(concert=concert).order_by("position")
    form = CommentForm()
    
    if request.method == "POST" and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.concert = concert
            comment.save()
            form = CommentForm() 
            
    return render(request, "concert.html", {"concert": concert, "comments": comments, "setlist": setlist, "form": form,
                                            })
