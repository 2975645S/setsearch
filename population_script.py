import logging
import os
from io import TextIOWrapper
from pathlib import Path
from typing import Generator

import django
import dotenv
import orjson
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Model
from zstandard import ZstdDecompressor

BATCH_SIZE = 100_000
GENRES_N = 100
DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger()


def setup_django():
    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wad.settings")
    django.setup()


def clean_db(models: list[type[Model]]):
    """Delete all records from the specified models."""
    for model in models:
        records = model.objects.all()
        logger.info(f"Deleting {records.count():,} records from {model.__name__}...")
        records.delete()


def migrate_db():
    """Make new migrations, and migrate the database."""
    call_command("makemigrations")
    call_command("migrate")
    logger.info("Database migrated successfully.")


def create_admin():
    """Create a default admin user if it doesn't exist."""
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )
        logger.info("Admin user created: username=admin, password=password123")
    else:
        logger.info("Admin user already exists, skipping creation.")


def read_zst(zstd: ZstdDecompressor, name: str) -> Generator[dict]:
    """Read a compressed .ndjson.zst file and return a list of dictionaries."""
    with open(DATA_DIR / f"{name}.ndjson.zst", "rb") as f, zstd.stream_reader(f) as reader:
        text_stream = TextIOWrapper(reader, encoding="utf-8")
        for line in text_stream:
            yield orjson.loads(line)


def create_artists(zstd: ZstdDecompressor):
    """Create artists from the compressed dataset."""
    # insert individually to trigger slug generation
    for data in read_zst(zstd, "artists"):
        artist = Artist(mbid=data["mbid"], name=data["name"], picture=data["picture"])
        logger.debug(f"Creating artist: {artist.name} ({artist.mbid})")
        artist.save()


def create_songs(zstd: ZstdDecompressor):
    """Create songs from the compressed dataset."""
    artists = Artist.objects.in_bulk(field_name="mbid")
    songs = []

    for data in read_zst(zstd, "songs"):
        artist = artists.get(data["artist"])
        if not artist:
            continue

        songs.append(
            Song(
                mbid=data["mbid"],
                title=data["title"],
                artist_id=artist.mbid,
                picture=data["picture"]
            )
        )

    logger.info(f"Creating {len(songs):,} songs in batches of {BATCH_SIZE:,}...")

    Song.objects.bulk_create(
        songs,
        batch_size=BATCH_SIZE,
        ignore_conflicts=True,
    )

    logger.info("Songs created successfully.")


if __name__ == "__main__":
    setup_django()
    from setsearch.models import *

    logger.info("=== MIGRATE ===")
    migrate_db()

    logger.info("=== CLEAN ===")
    clean_db([Artist, Song])

    logger.info("=== CREATE ADMIN USER ===")
    create_admin()

    logger.info("=== POPULATE ARTISTS AND SONGS ===")
    zstd = ZstdDecompressor()
    create_artists(zstd)
    create_songs(zstd)
