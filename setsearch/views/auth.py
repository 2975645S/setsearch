from typing import Callable, TypeVar

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from setsearch.forms.auth import SignUpForm, LoginForm, ProfileForm
from setsearch.models import User, Attendance

F = TypeVar("F")


def auth_page(request: HttpRequest, template: str, form_cls: type[F], get_user: Callable[[F], User]) -> HttpResponse:
    """Generic authentication page for both signup and login."""
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = form_cls(request.POST)

        if form.is_valid():
            user = get_user(form)
            login(request, user)
            return redirect(next_url or "home")
    else:
        form = form_cls()

    return render(request, f"{template}.html", {"form": form, "next": next_url})


def signup_page(request: HttpRequest) -> HttpResponse:
    return auth_page(request, "signup", SignUpForm, lambda form: form.save())
def login_page(request: HttpRequest) -> HttpResponse:
    return auth_page(request, "login", LoginForm, lambda form: form.cleaned_data["user"])

def logout(request: HttpRequest) -> HttpResponse:
    """Logs out the user and redirects to the home page."""
    from django.contrib.auth import logout

    next_url = request.GET.get("next") or request.POST.get("next")
    logout(request)

    return redirect(next_url or "home")

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    user = request.user
    concerts = []

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            login(request, user)
            return redirect("profile")
    else:
        attendances = Attendance.objects.filter(user=user)
        concerts = [attendance.concert for attendance in attendances]
        form = ProfileForm(instance=user)

    return render(request, "profile.html", {"form": form, "concerts": concerts})