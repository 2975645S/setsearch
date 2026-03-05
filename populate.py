import os
from io import BytesIO
from pathlib import Path

import django
import dotenv
import pandas as pd
from django.contrib.auth import get_user_model
from zstandard import ZstdDecompressor

BATCH_SIZE = 10_000
GENRES_N = 100
DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"


def setup_django():
    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wad.settings")
    django.setup()


def create_superuser():
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )


def create_artists(dctx):
    from setsearch.models import Artist

    with open(DATA_DIR / "artists.ndjson.zst", "rb") as f:
        df = pd.read_json(BytesIO(dctx.decompress(f.read())), lines=True)

    artists = [
        Artist(mbid=row["mbid"], name=row["name"])
        for row in df.to_dict("records")
    ]

    Artist.objects.bulk_create(
        artists,
        batch_size=BATCH_SIZE,
        ignore_conflicts=True,
    )


def create_songs_and_genres(dctx):
    from setsearch.models import Genre, Artist, Song

    with open(DATA_DIR / "songs.ndjson.zst", "rb") as f:
        df = pd.read_json(BytesIO(dctx.decompress(f.read())), lines=True)

    rows = df.to_dict("records")

    # determine top genres
    all_genres = set()
    for row in rows:
        tags = row.get("genres")
        if tags:
            all_genres.update(tags)

    # create genres
    Genre.objects.bulk_create(
        [Genre(name=g) for g in all_genres],
        batch_size=BATCH_SIZE,
        ignore_conflicts=True,
    )

    genre_map = {g.name: g.id for g in Genre.objects.all()}

    # create songs
    artist_map = Artist.objects.in_bulk(field_name="mbid")

    songs = []
    for row in rows:
        artist = artist_map.get(row["artist_mbid"])
        if not artist:
            continue

        songs.append(
            Song(
                track_mbid=row["track_mbid"],
                release_mbid=row["release_mbid"],
                title=row["title"],
                artist_id=artist.mbid,
            )
        )

    Song.objects.bulk_create(
        songs,
        batch_size=BATCH_SIZE,
        ignore_conflicts=True,
    )

    # relate genres to songs
    song_map = Song.objects.in_bulk(field_name="track_mbid")
    through = Song.genres.through

    buffer = []

    for row in rows:
        song = song_map.get(row["track_mbid"])
        if not song:
            continue

        tags = row.get("genres")
        if not tags:
            continue

        for g in tags:
            gid = genre_map.get(g)
            if gid:
                buffer.append(
                    through(
                        song_id=song.track_mbid,
                        genre_id=gid,
                    )
                )

        if len(buffer) >= BATCH_SIZE:
            through.objects.bulk_create(
                buffer,
                batch_size=BATCH_SIZE,
                ignore_conflicts=True,
            )
            buffer.clear()

    if buffer:
        through.objects.bulk_create(
            buffer,
            batch_size=BATCH_SIZE,
            ignore_conflicts=True,
        )


if __name__ == "__main__":
    dctx = ZstdDecompressor()

    setup_django()
    create_superuser()
    create_artists(dctx)
    create_songs_and_genres(dctx)
