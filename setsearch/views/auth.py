from typing import Callable, TypeVar

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from setsearch.forms import SignUpForm, LoginForm
from setsearch.models import User

F = TypeVar("F")


def auth_page(request: HttpRequest, template: str, form_cls: type[F], get_user: Callable[[F], User]) -> HttpResponse:
    """Generic authentication page for both signup and login."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = form_cls(request.POST)

        if form.is_valid():
            user = get_user(form)
            login(request, user)
            return redirect("home")
    else:
        form = form_cls()

    return render(request, f"{template}.html", {"form": form})


def signup_page(request: HttpRequest) -> HttpResponse:
    return auth_page(request, "signup", SignUpForm, lambda form: form.save())
def login_page(request: HttpRequest) -> HttpResponse:
    return auth_page(request, "login", LoginForm, lambda form: form.cleaned_data["user"])

def logout(request: HttpRequest) -> HttpResponse:
    """Logs out the user and redirects to the home page."""
    from django.contrib.auth import logout
    logout(request)
    return redirect("home")