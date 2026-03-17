from django.template import Library, Context
from django.urls import reverse
from django.utils.html import format_html

register = Library()

@register.simple_tag(takes_context=True)
def nav_link(context: Context, view_name: str, label: str, next: bool = False) -> str:
    request = context["request"]
    url = reverse(view_name)
    clazz = "nav-link"

    if request.path == url:
        clazz += " active"
    if next:
        if request.path != url:
            url += f"?next={request.path}"

    return format_html('<a class="{}" href="{}">{}</a>', clazz, url, label)
