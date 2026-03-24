from functools import wraps
from http import HTTPStatus
from typing import Literal

from django.forms import Form
from django.http import HttpRequest, HttpResponse

Source = Literal["GET", "POST"]


def api(form_class: type[Form], source: Source = "POST", key: str = "data"):
    """Decorator for API views that validates form data and ensures authentication."""
    if source not in ("GET", "POST"):
        raise ValueError("Source must be 'GET' or 'POST'")

    def decorator(view):
        @wraps(view)
        def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # make sure user is authenticated
            if not request.user.is_authenticated:
                return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

            # determine data source
            match source:
                case "GET":
                    data = request.GET
                case "POST":
                    data = request.POST

            # validate form data
            form = form_class(data)
            if not form.is_valid():
                return HttpResponse(form.errors.as_json(), status=HTTPStatus.BAD_REQUEST)
            kwargs[key] = form.cleaned_data

            return view(request, *args, **kwargs)

        return wrapped

    return decorator
