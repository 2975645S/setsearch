from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_GET

from setsearch.forms.concert import CreateConcertForm, EditConcertForm, SetlistForm
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
                  {"concert": concert, "comments": comments, "setlist": setlist, "attendees": attendees,
                   "rating": rating})


@login_required
@require_GET
def edit_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    concert = get_object_or_404(Concert, slug=concert_slug, artist__slug=artist_slug)

    # only the artist and admins can edit this concert
    if concert.verified and not (request.user.is_superuser or request.user == concert.artist.user):
        return redirect("concert", artist_slug=artist_slug, concert_slug=concert_slug)

    setlist = SetlistEntry.objects.filter(concert=concert).order_by("position")

    edit_form = EditConcertForm(instance=concert)
    setlist_form = SetlistForm(concert.artist)

    return render(request, "edit_concert.html",
                  {"concert": concert, "setlist": setlist, "edit_form": edit_form, "setlist_form": setlist_form})
