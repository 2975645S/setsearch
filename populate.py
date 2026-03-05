import os
from pathlib import Path

import django
import dotenv
import pandas as pd

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"


def setup_django():
    """Set up Django environment for standalone script."""

    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wad.settings")
    django.setup()


def create_artists():
    """Create Artist objects from the artists.ndjson file."""
    df = pd.read_json(DATA_DIR / "artists.ndjson", lines=True)

    for _, row in df.iterrows():
        Artist.objects.get_or_create(mbid=row["mbid"], name=row["name"])


if __name__ == "__main__":
    setup_django()
    from setsearch.models import Artist

    create_artists()
