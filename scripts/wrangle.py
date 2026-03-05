# todo: download artist pics from wikidata

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
            release_mbid = release.get("id")

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

                    tags = recording.get("tags", [])
                    genres = [tag["name"] for tag in tags]

                    for credit in recording.get("artist-credit", []):
                        artist = credit.get("artist")
                        if artist and artist.get("id") in mbids:
                            artist_mbid = artist["id"]
                            seen.add(track_mbid)
                            rows.append({
                                "track_mbid": track_mbid,
                                "release_mbid": release_mbid,
                                "artist_mbid": artist_mbid,
                                "title": title,
                                "genres": genres
                            })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    cctx = ZstdCompressor(level=19)

    # wrangle artists
    artists = load_artists()
    with open(DATA_DIR / "artists.ndjson.zst", "wb") as f:
        data = artists.to_json(orient="records", lines=True).encode("utf-8")
        f.write(cctx.compress(data))

    # wrangle releases
    artist_ids = set(artists["mbid"])
    songs = load_songs(artist_ids)
    with open(DATA_DIR / "songs.ndjson.zst", "wb") as f:
        data = songs.to_json(orient="records", lines=True).encode("utf-8")
        f.write(cctx.compress(data))
