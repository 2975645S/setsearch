"""
This script takes quite a while to run, and assumes you have downloaded the `artist`,`event` and `release` data dumps
from MusicBrainz at https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/ and placed them in `data/downloaded`.

These dumps are large, totaling over 300GB, and data is gathered from external sources, so the script outputs a
compressed, collated dataset of its results in the `data` directory, so you don't need to run it yourself.
It is included solely for reproducibility.
"""
from io import TextIOWrapper
from pathlib import Path

import orjson
from zstandard import ZstdCompressor
from zstandard.backend_c import ZstdDecompressor

from data.wrangler.events import load_events
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

    # # artists
    # artists = load_artists(http, DATA_DIR / "downloaded" / "artist")
    # write(zstd, "artists", artists)
    #
    # # songs + covers
    # artist_ids = set(artist.mbid for artist in artists)
    # songs, cover_refs = load_songs(DATA_DIR / "downloaded" / "release", artist_ids)
    # covers = fetch_all_covers(http, cover_refs)
    #
    # for song in songs:
    #     song.picture = covers.get(song.mbid)
    #
    # write(zstd, "songs", songs)


    artist_ids = set()
    dctx = ZstdDecompressor()

    with open(DATA_DIR / "artists.ndjson.zst", "rb") as f, dctx.stream_reader(f) as reader:
        for line in TextIOWrapper(reader, encoding="utf-8"):
            artist = orjson.loads(line)
            artist_ids.add(artist.get("mbid"))

    print(artist_ids)
    concerts = load_events(DATA_DIR / "downloaded" / "event", artist_ids)
    write(zstd, "concerts", concerts)