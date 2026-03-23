from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from setsearch.forms.concert import CreateConcertForm, EditConcertForm
from setsearch.models import Concert, Comment, SetlistEntry, Artist, Attendance


@login_required
def create_concert(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CreateConcertForm(request.POST)
        if form.is_valid():
            concert = form.save(commit=False)
            concert.modified_by = request.user
            concert.save()
            return redirect("concert", artist_slug=concert.artist.slug, concert_slug=concert.slug)
    else:
        artist_slug = request.GET.get("artist")
        initial = {}

        if artist_slug:
            artist = get_object_or_404(Artist, slug=artist_slug)
            initial["artist"] = artist.id

        form = CreateConcertForm(initial=initial)

    return render(request, "create_concert.html", {"form": form})


def view_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    concert = get_object_or_404(Concert, slug=concert_slug, artist__slug=artist_slug)
    comments = Comment.objects.filter(concert=concert).order_by("timestamp")
    setlist = SetlistEntry.objects.filter(concert=concert).order_by("position")
    attendees = Attendance.objects.filter(concert=concert).count()
    rating = None

    if request.user.is_authenticated:
        try:
            attendance = Attendance.objects.get(concert=concert, user=request.user)
            rating = attendance.rating or 0
        except Attendance.DoesNotExist:
            pass

    return render(request, "concert.html",
                  {"concert": concert, "comments": comments, "setlist": setlist, "attendees": attendees, "rating": rating})

@login_required
def edit_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    concert = get_object_or_404(Concert, slug=concert_slug, artist__slug=artist_slug)

    if request.method == "POST":
        edit_form = EditConcertForm(request.POST, instance=concert)
        print(edit_form)
        if edit_form.is_valid():
            concert = edit_form.save(commit=False)
            concert.modified_by = request.user
            concert.save()
            return redirect("concert", artist_slug=concert.artist.slug, concert_slug=concert.slug)
    else:
        edit_form = EditConcertForm(instance=concert)

    return render(request, "edit_concert.html", {"concert": concert, "edit_form": edit_form})