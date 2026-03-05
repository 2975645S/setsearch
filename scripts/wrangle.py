import os
from pathlib import Path

import kagglehub
import pandas as pd

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent.parent / "data"


def load_artists():
    """Load popularity data for artists."""
    path = kagglehub.dataset_download("pieca111/music-artists-popularity") + "/artists.csv"
    df = pd.read_csv(path, low_memory=False, usecols=["mbid", "artist_mb", "listeners_lastfm", "ambiguous_artist"],
                     dtype={"mbid": str, "artist_mb": str, "listeners_lastfm": float, "ambiguous_artist": bool})
    return df


def save_artists(df):
    """Save the most popular artists to a ndjson file."""
    df = df.dropna(subset=["mbid", "artist_mb"])  # only artists with valid mbid and name
    df = df[~df["ambiguous_artist"]].reset_index(drop=True)  # remove ambiguous artists

    # keep only the top 0.1% of artists
    cutoff = df["listeners_lastfm"].quantile(1 - 0.001)
    df = df[df["listeners_lastfm"] >= cutoff].reset_index(drop=True)

    # reformat dataframe
    df = df.drop(columns=["listeners_lastfm", "ambiguous_artist"])
    df = df.rename(columns={"artist_mb": "name"})

    # save to ndjson
    df.to_json(DATA_DIR / "artists.ndjson", orient="records", lines=True)


if __name__ == "__main__":
    # make sure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # wrangle artists
    artists = load_artists()
    save_artists(artists)
