"""
This script takes quite a while to run, and assumes you have downloaded the `artist` and `release` data dumps from
MusicBrainz at https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/ and placed them in `data/downloaded`.

These dumps are large, totaling over 300GB, and data is gathered from external sources, so the script outputs a
compressed, collated dataset of its results in the `data` directory, so you don't need to run it yourself.
It is included solely for reproducibility.
"""

from pathlib import Path

import orjson
from zstandard import ZstdCompressor

from data.wrangler.artists import load_artists
from data.wrangler.cover_art import fetch_all_covers
from data.wrangler.songs import load_songs
from data.wrangler.util import get_http

COMPRESSION_LEVEL = 19

DATA_DIR = Path(__file__).resolve().parent.parent

def write(zstd: ZstdCompressor, name: str, data: list[object]):
    """Write a list of objects to a zstd-compressed ndjson file."""
    with open(DATA_DIR / f"{name}.ndjson.zst", "wb") as f, zstd.stream_writer(f) as writer:
        for item in data:
            writer.write(orjson.dumps(item))
            writer.write(b"\n")


if __name__ == "__main__":
    # setup
    http = get_http()
    zstd = ZstdCompressor(level=COMPRESSION_LEVEL)

    # artists
    artists = load_artists(http, DATA_DIR / "downloaded" / "artist")
    write(zstd, "artists", artists)

    # songs + covers
    artist_ids = set(artist.mbid for artist in artists)
    songs, cover_refs = load_songs(DATA_DIR / "downloaded" / "release", artist_ids)
    covers = fetch_all_covers(http, cover_refs)

    for song in songs:
        song.picture = covers.get(song.mbid)

    write(zstd, "songs", songs)