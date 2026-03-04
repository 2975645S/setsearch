from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def hello(request: HttpRequest, name: str = "World") -> HttpResponse:
    return render(request, "hello.html", {"name": name})
