# todo: download artist pics from wikidata
# todo: genres

import os
from pathlib import Path
from typing import Set

import kagglehub
import orjson
import pandas as pd
from zstandard import ZstdCompressor

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent.parent / "data"
DOWNLOADED_DIR = DATA_DIR / "downloaded"


def load_artists() -> pd.DataFrame:
    """Load popularity data for artists."""
    path = kagglehub.dataset_download("pieca111/music-artists-popularity") + "/artists.csv"
    df = pd.read_csv(path, low_memory=False, usecols=["mbid", "artist_mb", "listeners_lastfm", "ambiguous_artist"],
                     dtype={"mbid": str, "artist_mb": str, "listeners_lastfm": float, "ambiguous_artist": bool})

    df = df.dropna(subset=["mbid", "artist_mb"])  # only artists with valid mbid and name
    df = df[~df["ambiguous_artist"]].reset_index(drop=True)  # remove ambiguous artists

    # keep the top 100 artists
    df = df.nlargest(100, "listeners_lastfm").reset_index(drop=True)

    # reformat dataframe
    df = df.drop(columns=["listeners_lastfm", "ambiguous_artist"])
    df = df.rename(columns={"artist_mb": "name"})

    return df


def load_songs(mbids: Set[str]) -> pd.DataFrame:
    rows = []
    seen = set()

    # don't load with pandas, will deserialize unimportant data,
    # and we really can't afford that with a 300gb dataset :(
    with open(DOWNLOADED_DIR / "release", "rb") as f:
        for line in f:
            release = orjson.loads(line)

            for media in release.get("media", []):
                for track in media.get("tracks", []):
                    recording = track.get("recording")
                    if not recording:
                        continue

                    track_mbid = recording.get("id")
                    title = recording.get("title")
                    if not track_mbid or not title:
                        continue
                    if track_mbid in seen:
                        continue

                    for credit in recording.get("artist-credit", []):
                        artist = credit.get("artist")
                        if artist and artist.get("id") in mbids:
                            artist_mbid = artist["id"]
                            seen.add(track_mbid)
                            rows.append({
                                "mbid": track_mbid,
                                "title": title,
                                "artist_mbid": artist_mbid
                            })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    cctx = ZstdCompressor(level=19)

    # wrangle artists
    artists = load_artists().to_json(orient="records", lines=True).encode("utf-8")
    artists = cctx.compress(artists)
    with open(DATA_DIR / "artists.ndjson.zst", "wb") as f:
        f.write(artists)

    # wrangle releases
    artist_ids = set(artists["mbid"].tolist())
    songs = load_songs(artist_ids).to_json(orient="records", lines=True).encode("utf-8")
    songs = cctx.compress(songs)
    with open(DATA_DIR / "songs.ndjson.zst", "wb") as f:
        f.write(songs)
