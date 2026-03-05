# todo:
# consider compiling this data and including it in the repository
# instead of making users download it

import os

import django
import dotenv
import kagglehub
import pandas as pd


def setup_django():
    """Set up Django environment for standalone script."""

    dotenv.load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wad.settings")
    django.setup()


def load_artists():
    """Load a list of the top 1% most popular artists."""

    path = kagglehub.dataset_download("pieca111/music-artists-popularity") + "/artists.csv"
    df = pd.read_csv(path, low_memory=False, usecols=["mbid", "artist_mb", "listeners_lastfm", "ambiguous_artist"],
                     dtype={"mbid": str, "artist_mb": str, "listeners_lastfm": float, "ambiguous_artist": bool})

    df = df.rename(columns={"artist_mb": "name"})
    df = df.dropna(subset=["mbid", "name"])

    # remove ambiguous artists
    df = df[~df["ambiguous_artist"]].reset_index(drop=True)

    # keep only the top 1% of artists (~10k artists)
    cutoff = df["listeners_lastfm"].quantile(0.99)
    df = df[df["listeners_lastfm"] >= cutoff].reset_index(drop=True)

    df = df.drop(columns=["listeners_lastfm", "ambiguous_artist"])
    return df


def save_artists(df):
    """Save artists to the database."""

    for _, row in df.iterrows():
        Artist.objects.get_or_create(mbid=row["mbid"], name=row["name"])


if __name__ == "__main__":
    setup_django()

    from setsearch.models import Artist

    artists = load_artists()
    save_artists(artists)
