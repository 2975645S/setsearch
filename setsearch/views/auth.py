from typing import Callable, TypeVar

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from setsearch.forms.auth import SignUpForm, LoginForm, ProfileForm
from setsearch.models import User, Concert

F = TypeVar("F")


def auth_page(request: HttpRequest, template: str, form_cls: type[F], get_user: Callable[[F], User]) -> HttpResponse:
    """Authentication page for both login and signup. Renders the appropriate form and handles form submission."""
    next_url = request.GET.get("next") or request.POST.get("next") or "home"

    # user is already authenticated, no need to show the form
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == "POST":
        form = form_cls(request.POST)

        if form.is_valid():
            user = get_user(form)
            login(request, user)
            return redirect(next_url)
    else:
        form = form_cls()

    return render(request, f"{template}.html", {"form": form, "next": next_url})


def signup_page(request: HttpRequest) -> HttpResponse:
    """Page for signing up for a new account."""
    return auth_page(request, "signup", SignUpForm, lambda form: form.save())


def login_page(request: HttpRequest) -> HttpResponse:
    """Page for logging in to an existing account."""
    return auth_page(request, "login", LoginForm, lambda form: form.cleaned_data["user"])


@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    """Logs out the user and redirects to the home page."""
    from django.contrib.auth import logout
    logout(request)

    next_url = request.GET.get("next") or "home"
    return redirect(next_url)


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """Page for viewing and editing the user's profile, as well as viewing attended concerts."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # re-login the user to update the session with the new user data
            login(request, request.user)
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    concerts = Concert.objects.filter().filter(attendance__user=request.user).select_related("artist",
                                                                                             "venue").order_by("-date")

    return render(request, "profile.html", {"form": form, "concerts": concerts})
