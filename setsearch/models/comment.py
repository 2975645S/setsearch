from django.db.models import Model, ForeignKey, Index, CASCADE
from django.db.models.fields import CharField, DateTimeField
from django.utils import timezone

from setsearch.models.concert import Concert
from setsearch.models.user import User


class Comment(Model):
    """A user commented on a concert."""

    user = ForeignKey(User, on_delete=CASCADE)
    concert = ForeignKey(Concert, on_delete=CASCADE)
    content = CharField(max_length=1000)
    timestamp = DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

        indexes = [
            Index(fields=["concert", "timestamp"]),  # get comments for concert, ordered by timestamp
        ]