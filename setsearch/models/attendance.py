from django.db.models import Model, ForeignKey, Index, CASCADE
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import SmallIntegerField

from setsearch.models.concert import Concert
from setsearch.models.user import User


class Attendance(Model):
    """
    A user has attended a concert.

    Attributes:
        user: The user who attended the concert.
        concert: The concert that was attended.
        rating: The user's rating of the concert on a 5-star scale.
    """

    user = ForeignKey(User, on_delete=CASCADE)
    concert = ForeignKey(Concert, on_delete=CASCADE)
    rating = SmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "attendance"
        verbose_name_plural = "attendances"

        constraints = [
            UniqueConstraint(fields=["user", "concert"], name="unique_user_concert")
        ]
        indexes = [
            Index(fields=["user", "concert"])  # has user attended concert?
        ]
