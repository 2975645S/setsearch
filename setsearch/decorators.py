from functools import wraps
from http import HTTPStatus

from django.forms import Form
from django.http import HttpRequest, HttpResponse


def api(form_class: type[Form], key: str = "data"):
    """Decorator for API views that validates form data and ensures authentication."""

    def decorator(view):
        @wraps(view)
        def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # make sure user is authenticated
            if not request.user.is_authenticated:
                return HttpResponse(status=HTTPStatus.UNAUTHORIZED)

            # validate form data
            form = form_class(request.POST)
            if not form.is_valid():
                return HttpResponse(form.errors.as_json(), status=HTTPStatus.BAD_REQUEST)
            kwargs[key] = form.cleaned_data

            return view(request, *args, **kwargs)

        return wrapped

    return decorator
