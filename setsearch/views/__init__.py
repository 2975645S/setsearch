from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .api import *
from .artist import *
from .auth import *
from .concert import *


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")