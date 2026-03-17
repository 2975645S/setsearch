from typing import TypeVar

from django.db.models import Model
from django.template.defaultfilters import slugify

M = TypeVar("M", bound=Model)

def unique_slug(instance: M, field: str, value: str) -> str:
    slug = slugify(value)
    unique = slug
    n = 1
    model = instance.__class__

    # increment n until slug is unique for field in model
    while model.objects.filter(**{field: unique}).exists():
        unique = f"{slug}-{n}"
        n += 1

    return unique