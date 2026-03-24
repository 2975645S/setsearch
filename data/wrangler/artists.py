from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import kagglehub
import orjson
import pandas as pd
from requests import Session

from data.wrangler.util import get_logger

ARTISTS_TO_KEEP = 100
MAX_WORKERS = 8  # fewer than 10 concurrent, below 20 average per second
PROGRESS_INTERVAL = 1000

POPULARITY_TYPES = {
    "mbid": str,
    "artist_mb": str,
    "listeners_lastfm": float,
    "ambiguous_artist": bool
}

logger = get_logger()


@dataclass
class Artist:
    mbid: str
    name: str
    picture: str | None = None


def get_popular_artists() -> list[str]:
    """Get the MusicBrainz IDs of the most popular artists from the Kaggle dataset."""
    path = kagglehub.dataset_download("pieca111/music-artists-popularity") + "/artists.csv"
    df = pd.read_csv(path, low_memory=False, usecols=POPULARITY_TYPES.keys(), dtype=POPULARITY_TYPES)
    df = df[~df["ambiguous_artist"]].reset_index(drop=True)  # remove ambiguous artists
    df = df.dropna(subset=["mbid", "artist_mb"])  # only artists with valid mbid and name
    df = df.nlargest(ARTISTS_TO_KEEP, "listeners_lastfm").reset_index(drop=True)  # keep the top artists
    ids = df["mbid"].values.tolist()
    return ids


def find_artist_picture(http: Session, artist: dict) -> str | None:
    """Find the artist's picture by looking for a wikidata relation and fetching the image from there."""
    relations = artist.get("relations", [])

    for relation in relations:
        # we want to fetch the image from wikidata
        if not relation.get("type") == "wikidata":
            continue

        # find the entity on wikidata
        url = relation.get("url", {}).get("resource")
        if url:
            entity_id = url.split("/")[-1]
            res = http.get(f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json", timeout=10)

            if res.status_code == 200:
                data = res.json()

                # get the image claim (P18)
                entity = data.get("entities", {}).get(entity_id, {})
                image_claim = entity.get("claims", {}).get("P18", [{}])[0]
                image_name = image_claim.get("mainsnak", {}).get("datavalue", {}).get("value")

                return image_name

    return None


def load_artists(http: Session, path: Path) -> list[Artist]:
    """Load artists from the MusicBrainz dataset, keeping only the most popular ones."""
    popular = get_popular_artists()
    artists = []
    futures = []
    read_count, kept_count = 0, 0

    with open(path, "rb") as f, ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for line in f:
            read_count += 1

            if read_count % PROGRESS_INTERVAL == 0:
                logger.info(f"Read {read_count}, kept {kept_count} artists")

            artist = orjson.loads(line)
            mbid = artist.get("id")

            # we only care about the most popular artists
            if mbid not in popular:
                continue
            kept_count += 1

            name = artist.get("name")
            artists.append(Artist(mbid, name))
            futures.append(pool.submit(find_artist_picture, http, artist))

            if kept_count >= ARTISTS_TO_KEEP:
                break

        logger.info("Finished processing artists, now fetching pictures...")

        for i, fut in enumerate(futures):
            artists[i].picture = fut.result()

    logger.info("Finished fetching artist pictures.")
    return artists
