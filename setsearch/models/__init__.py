from django.contrib.auth import get_user_model

from .artist import Artist
from .attendance import Attendance
from .comment import Comment
from .concert import Concert
from .setlist import SetlistEntry
from .song import Song
from .venue import Venue

User = get_user_model()