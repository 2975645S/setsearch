import os
from pathlib import Path
from typing import Set

import kagglehub
import orjson
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from zstandard import ZstdCompressor

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent.parent / "data"
DOWNLOADED_DIR = DATA_DIR / "downloaded"

# https://wikitech.wikimedia.org/wiki/Robot_policy
HEADERS = {
    "User-Agent": "SetSearch/0.0 (2975645S@student.gla.ac.uk) requests/2.32.5",
    "Accept-Encoding": "gzip"
}



def load_artists() -> pd.DataFrame:
    # get most popular artists
    path = kagglehub.dataset_download("pieca111/music-artists-popularity") + "/artists.csv"
    df = pd.read_csv(path, low_memory=False, usecols=["mbid", "artist_mb", "listeners_lastfm", "ambiguous_artist"],
                     dtype={"mbid": str, "artist_mb": str, "listeners_lastfm": float, "ambiguous_artist": bool})
    df = df.dropna(subset=["mbid", "artist_mb"])  # only artists with valid mbid and name
    df = df[~df["ambiguous_artist"]].reset_index(drop=True)  # remove ambiguous artists
    df = df.nlargest(100, "listeners_lastfm").reset_index(drop=True) # keep the top 100 artists
    popular_mbids = df["mbid"].values

    # combine with musicbrainz data
    rows = []

    with open(DOWNLOADED_DIR / "artist", "rb") as f:
        for line in f:
            artist = orjson.loads(line)
            mbid = artist.get("id")
            if mbid not in popular_mbids:
                continue

            relations = artist.get("relations", [])
            image_name = None

            for relation in relations:
                if relation.get("type") == "wikidata":
                    url = relation.get("url", {}).get("resource")
                    if url:
                        adapter = HTTPAdapter(max_retries=Retry(
                            total=5,  # max retries
                            backoff_factor=1,  # wait = backoff_factor * (2 ** (retry_number - 1))
                            status_forcelist=[429, 500, 502, 503, 504],  # retry these HTTP codes
                            raise_on_status=False
                        ))
                        session = requests.Session()
                        session.mount("https://", adapter)

                        entity = url.split("/")[-1]
                        data = session.get(f"https://www.wikidata.org/wiki/Special:EntityData/{entity}.json", headers=HEADERS, timeout=10)

                        if data.status_code == 200:
                            data = data.json()
                            claims = data.get("entities", {}).get(entity, {}).get("claims", {})
                            image_name = claims.get("P18", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value")

            rows.append({
                "mbid": mbid,
                "name": artist.get("name"),
                "picture": image_name
            })

    return pd.DataFrame(rows)


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

                    tags = recording.get("tags", [])
                    genres = [tag["name"] for tag in tags]

                    for credit in recording.get("artist-credit", []):
                        artist = credit.get("artist")
                        if artist and artist.get("id") in mbids:
                            seen.add(track_mbid)
                            rows.append({
                                "track_mbid": track_mbid,
                                "release_mbid": release.get("id"),
                                "artist_mbid": artist["id"],
                                "title": title,
                                "genres": genres
                            })

    return pd.DataFrame(rows)

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
