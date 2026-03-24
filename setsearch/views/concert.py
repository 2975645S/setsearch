from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_GET

from setsearch.forms.concert import CreateConcertForm, EditConcertForm, SetlistForm
from setsearch.models import Concert, Comment, SetlistEntry, Artist, Attendance


@login_required
def create_concert(request: HttpRequest) -> HttpResponse:
    """Page for creating a new concert."""
    if request.method == "POST":
        # POST form
        form = CreateConcertForm(request.POST)

        if form.is_valid():
            # create concert
            concert = form.save(commit=False)
            concert.modified_by = request.user
            concert.save()

            # redirect to the new concert page
            return redirect("concert", artist_slug=concert.artist.slug, concert_slug=concert.slug)
    else:
        # GET
        # pre-fill the artist if a slug is provided in the query  params
        artist_slug = request.GET.get("artist")
        initial = {}

        if artist_slug:
            artist = get_object_or_404(Artist, slug=artist_slug)
            initial["artist"] = artist.id

        form = CreateConcertForm(initial=initial)

    return render(request, "create_concert.html", {"form": form})


@require_GET
def view_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    """Concert page displaying details, comments, setlist, and attendance info."""
    # fetch data
    concert = get_object_or_404(Concert.objects.select_related("artist", "venue"), artist__slug=artist_slug,
                                slug=concert_slug)
    comments = Comment.objects.filter(concert=concert).select_related("user").order_by("timestamp")
    setlist = SetlistEntry.objects.filter(concert=concert).select_related("song").order_by("position")

    attendance_qs = Attendance.objects.filter(concert=concert)
    attendees = attendance_qs.count()

    # determine the user's rating if they are logged in
    rating = None

    if request.user.is_authenticated:
        attendance = attendance_qs.filter(user=request.user).only("rating").first()
        rating = attendance.rating or 0 if attendance else None

    return render(request, "concert.html",
                  {"concert": concert, "comments": comments, "setlist": setlist, "attendees": attendees,
                   "rating": rating})


@login_required
@require_GET
def edit_concert(request: HttpRequest, artist_slug: str, concert_slug: str) -> HttpResponse:
    """Page for editing an existing concert. Uses /api/concerts/update for saving changes on the client-side."""
    concert = get_object_or_404(Concert.objects.select_related("artist__user"), slug=concert_slug,
                                artist__slug=artist_slug)

    # only the artist and admins can edit this concert
    is_artist = request.user == concert.artist.user
    is_admin = request.user.is_superuser
    can_edit = is_admin or is_artist

    if concert.verified and not can_edit:
        return redirect("concert", artist_slug=artist_slug, concert_slug=concert_slug)

    setlist = SetlistEntry.objects.filter(concert=concert).select_related("song").order_by("position")
    edit_form = EditConcertForm(instance=concert)
    setlist_form = SetlistForm(concert.artist)

    return render(request, "edit_concert.html",
                  {"concert": concert, "setlist": setlist, "form": edit_form, "setlist_form": setlist_form})


@require_GET
def upcoming_concerts(request: HttpRequest) -> HttpResponse:
    """Page listing all upcoming concerts."""
    today = timezone.now().date()
    concerts = Concert.objects.filter(date__isnull=False, date__gte=today).order_by("date")

    return render(request, "upcoming.html", {"concerts": concerts})
