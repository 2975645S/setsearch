from functools import wraps

from django.contrib.auth import login as auth_login
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from setsearch.forms import SignUpForm, LoginForm
from setsearch.models import Artist, Concert, Comment


def unauthenticated(view_func):
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapper


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


@unauthenticated
def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


@unauthenticated
def login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            auth_login(request, user)
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def artist(request: HttpRequest, slug: str) -> HttpResponse:
    # todo: handle 404 (done)
    artist = get_object_or_404(Artist, slug=slug)
    return render(request, "artist.html", {"artist": artist})


def artist_list(request: HttpRequest) -> HttpResponse:
    artists = Artist.objects.values("name", "slug")
    return JsonResponse(list(artists), safe=False)

def concerts(request: HttpRequest, concert_id: int) -> HttpResponse:
    concert = get_object_or_404(Concert, id=concert_id)
    comments = Comment.objects.filter(concert=concert).order_by("timestamp")
    return render(request, "concerts.html", {"concert": concert, "comments": comments})
