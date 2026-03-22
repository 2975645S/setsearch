from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from setsearch.models import Concert
from .api import *
from .artist import *
from .auth import *
from .concert import *


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def upcoming_concerts(request: HttpRequest) -> HttpResponse:
    today = timezone.now().date()
    concerts = Concert.objects.filter(
        Q(year__gt=today.year) |
        Q(year=today.year, month__gt=today.month) |
        Q(year=today.year, month=today.month, day__gte=today.day)
    ).order_by("year", "month", "day")

    return render(request, "upcoming.html", {"concerts": concerts})
