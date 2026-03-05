import os
from io import BytesIO
from pathlib import Path

import django
import dotenv
import pandas as pd
from django.contrib.auth import get_user_model
from zstandard import ZstdDecompressor

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"
BATCH_SIZE = 1000

def setup_django():
    """Set up Django environment for standalone script."""
    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wad.settings")
    django.setup()


def create_superuser():
    # noinspection PyPep8Naming
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(username="admin", email="admin@example.com", password="password123")


def create_artists(dctx: ZstdDecompressor):
    """Create Artist objects from the artists.ndjson file."""
    from setsearch.models import Artist

    with open(DATA_DIR / "artists.ndjson.zst", "rb") as f:
        data = dctx.decompress(f.read())
        df = pd.read_json(BytesIO(data), lines=True)

        artists = [Artist(mbid=row["mbid"], name=row["name"]) for _, row in df.iterrows()]
        Artist.objects.bulk_create(artists, batch_size=BATCH_SIZE, ignore_conflicts=True)

def create_songs(dctx: ZstdDecompressor):
    """Create Song objects from the songs.ndjson file."""
    from setsearch.models import Artist, Song

    with open(DATA_DIR / "songs.ndjson.zst", "rb") as f:
        data = dctx.decompress(f.read())
        df = pd.read_json(BytesIO(data), lines=True)

        artist_map = {a.mbid: a for a in Artist.objects.all()}
        songs = [Song(mbid=row["mbid"], title=row["title"], artist=artist_map[row["artist_mbid"]]) for _, row in
                 df.iterrows() if row["artist_mbid"] in artist_map]
        Song.objects.bulk_create(songs, batch_size=BATCH_SIZE, ignore_conflicts=True)

if __name__ == "__main__":
    dctx = ZstdDecompressor()
    setup_django()

    create_superuser()
    create_artists(dctx)
    create_songs(dctx)
