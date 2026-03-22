from django.forms.forms import Form
from django.forms.models import ModelChoiceField
from django_select2.forms import ModelSelect2Widget

from setsearch.models import User, Artist


class LinkToUserForm(Form):
    username = ModelChoiceField(queryset=User.objects.all(),
                                widget=ModelSelect2Widget(model=User, search_fields=["username__icontains"],
                                                          attrs={"data-minimum-input-length": 0, "data-placeholder": "N/A"}),
                                label="Link to user")

    def __init__(self, artist: Artist, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if artist and artist.user:
            self.fields["username"].initial = artist.user
