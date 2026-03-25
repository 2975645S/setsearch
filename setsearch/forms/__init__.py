from django.db.models import Model
from django.forms import Select, CharField
from django_select2.forms import Select2Mixin, Select2TagMixin


def article(word):
    return "an" if word[0].lower() in "aeiou" else "a"


class CreateModelField(CharField):
    def __init__(self, model: type[Model], input_field: str = "name", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = model
        self._pk = model._meta.pk.name
        self._input_field = input_field
        self.widget = CreateModelSelect2Widget(model, input_field)

    def prepare_value(self, value):
        if isinstance(value, self._model):
            return {
                "id": getattr(value, self._pk),
                "text": getattr(value, self._input_field)
            }
        return super().prepare_value(value)

    def clean(self, value):
        value = super().clean(value)
        if not value:
            return None

        # existing object (id)
        try:
            obj = self._model.objects.get(**{self._pk: value})
            return obj
        except (self._model.DoesNotExist, ValueError):
            pass

        # new object (name)
        obj, _ = self._model.objects.get_or_create(**{self._input_field: value})
        return obj


class CreateModelSelect2Widget(Select2Mixin, Select2TagMixin, Select):
    def __init__(self, model: type[Model], field: str = "name"):
        super().__init__()
        self._field = field
        self._model = model

    # refresh choices every time
    @property
    def choices(self):
        return [(a.id, getattr(a, self._field)) for a in self._model.objects.all()]

    @choices.setter
    def choices(self, value):
        # ignore external attempts to set choices
        return

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        name = self._model._meta.verbose_name
        attrs["data-placeholder"] = f"Search for {article(name)} {name}..."
        attrs["data-token-separators"] = '[","]'  # allow spaces
        return attrs
