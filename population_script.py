import logging
import os
from io import TextIOWrapper
from pathlib import Path
from typing import Generator

import django
import dotenv
import orjson
from django.core.management import call_command
from django.db.models import Model
from zstandard import ZstdDecompressor

BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(os.path.join(BASE_DIR / ".env"))

BATCH_SIZE = 100_000
GENRES_N = 100
DATA_DIR = BASE_DIR / "data"
PASSWORD = os.environ.get("PASSWORD", "password123")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger()


def setup_django():
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
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@setsearch.com",
            password=PASSWORD,
        )
        logger.info(f"Admin user created: username=admin, password={PASSWORD}")
    else:
        logger.info("Admin user already exists, skipping creation.")


def read_zst(zstd: ZstdDecompressor, name: str) -> Generator[dict]:
    """Read a compressed .ndjson.zst file and return a list of dictionaries."""
    with open(DATA_DIR / f"{name}.ndjson.zst", "rb") as f, zstd.stream_reader(f) as reader:
        text_stream = TextIOWrapper(reader, encoding="utf-8")
        for line in text_stream:
            yield orjson.loads(line)


def bulk_create(objects: list[Model]):
    clazz = objects[0].__class__
    logger.info(f"Creating {len(objects):,} {clazz.__name__}s in batches of {BATCH_SIZE:,}...")
    clazz.objects.bulk_create(objects, batch_size=BATCH_SIZE, ignore_conflicts=True)
    logger.info(f"{clazz.__name__}s created successfully.")


def create_artists(zstd: ZstdDecompressor) -> dict[str, "Artist"]:
    """Create artists from the compressed dataset."""
    artists = {}

    # insert individually to trigger slug generation
    for data in read_zst(zstd, "artists"):
        # create artist
        artist = Artist(mbid=data["mbid"], name=data["name"], picture=data["picture"])
        artist.save()

        # link to user
        artist.user = User.objects.create_user(username=artist.slug, email=f"{artist.slug}@setsearch.com",
                                               password=PASSWORD)
        artist.save()
        artists[artist.mbid] = artist

    logger.info("Artists created successfully.")
    return artists


def create_songs(zstd: ZstdDecompressor, artists: dict[str, "Artist"]) -> dict[str, "Song"]:
    """Create songs from the compressed dataset."""
    songs = []

    for data in read_zst(zstd, "songs"):
        artist = artists.get(data["artist"])
        if not artist:
            continue

        songs.append(Song(
            mbid=data["mbid"],
            title=data["title"],
            artist=artist,
            picture=data["picture"]
        ))

    bulk_create(songs)
    return {s.mbid: s for s in Song.objects.all()}


def create_venues(zstd: ZstdDecompressor) -> dict[str, "Venue"]:
    """Create venues from the compressed dataset."""
    venues = []

    for data in read_zst(zstd, "venues"):
        venues.append(Venue(mbid=data["mbid"], name=data["name"], city=data["city"], address=data["address"]))

    bulk_create(venues)
    return {v.mbid: v for v in Venue.objects.all()}


def create_concerts(zstd: ZstdDecompressor, artists: dict[str, "Artist"], venues: dict[str, "Venue"]) -> dict[
    str, "Concert"]:
    """Create concerts from the compressed dataset."""
    admin = User.objects.get(username="admin")
    concerts = {}

    # insert individually to trigger slug generation
    for data in read_zst(zstd, "concerts"):
        artist = artists.get(data["artist"])
        venue = venues.get(data["venue"])
        if not artist or not venue:
            continue

        concert = Concert(mbid=data["mbid"], artist=artist, name=data["name"],
                          venue=venue, modified_by=admin)
        concert.set_date(data["year"], data["month"], data["day"])

        concert.save()
        concerts[concert.mbid] = concert

    return concerts


def create_entries(zstd: ZstdDecompressor, songs: dict[str, "Song"], concerts: dict[str, "Concert"]):
    """Create setlist entries from the compressed dataset."""
    entries = []

    for data in read_zst(zstd, "setlist"):
        song = songs.get(data["song_mbid"])
        concert = concerts.get(data["concert_mbid"])
        if not song or not concert:
            continue

        entries.append(
            SetlistEntry(concert=concert, song=song, position=data["position"])
        )

    bulk_create(entries)


if __name__ == "__main__":
    setup_django()
    from setsearch.models import *

    logger.info("=== MIGRATE ===")
    migrate_db()

    logger.info("=== CLEAN ===")
    clean_db([User, Artist, Song, Venue, Concert])

    logger.info("=== CREATE ADMIN USER ===")
    create_admin()

    logger.info("=== POPULATE ARTISTS, SONGS, VENUES, CONCERTS, AND SETLIST ENTRIES ===")
    zstd = ZstdDecompressor()
    artists = create_artists(zstd)
    songs = create_songs(zstd, artists)
    venues = create_venues(zstd)
    concerts = create_concerts(zstd, artists, venues)
    create_entries(zstd, songs, concerts)

    logger.info("================================================")
    logger.info(f"The password for all created users is \"{PASSWORD}\".")
