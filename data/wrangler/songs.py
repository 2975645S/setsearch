from dataclasses import dataclass
from itertools import chain
from pathlib import Path

import orjson

from data.wrangler.util import get_logger

PROGRESS_INTERVAL = 10_000

logger = get_logger()


@dataclass(slots=True)
class CoverArtRef:
    song: str
    release: str
    release_group: str


@dataclass
class Song:
    mbid: str
    title: str
    artist: str
    picture: str | None = None


def load_songs(path: Path, artists: set[str]) -> tuple[list[Song], list[CoverArtRef]]:
    """Load songs from the MusicBrainz dataset by the artists we care about."""
    songs = []
    cover_refs = []
    seen = set()
    read_count, kept_count = 0, 0

    with open(path, "rb") as f:
        for line in f:
            read_count += 1

            if read_count % PROGRESS_INTERVAL == 0:
                logger.info(f"Read {read_count}, kept {kept_count} songs")

            release = orjson.loads(line)
            tracks = chain.from_iterable(media.get("tracks", []) for media in release.get("media", []))

            for track in tracks:
                recording = track.get("recording")
                if not recording:
                    continue

                # make sure we haven't seen the song before
                mbid = recording.get("id")
                if mbid in seen:
                    continue

                # if the recording is by one of the artists we care about, add it to the list
                for credit in recording.get("artist-credit", []):
                    artist = credit.get("artist")
                    if artist and artist.get("id") in artists:
                        kept_count += 1

                        # create cover art ref
                        release_group = release.get("release-group", {}).get("id")
                        cover_refs.append(CoverArtRef(mbid, release.get("id"), release_group))

                        # add the song to the list
                        seen.add(mbid)
                        song = Song(mbid, recording["title"], artist["id"])
                        songs.append(song)

    logger.info("Finished processing songs.")
    return songs, cover_refs
