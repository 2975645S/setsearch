import re
from dataclasses import dataclass
from pathlib import Path

import orjson

from data.wrangler.util import get_logger

PROGRESS_INTERVAL = 100
LINE_RE = re.compile(r"^([@*#])\s+(.*)$")
MB_LINK_RE = re.compile(r"\[([0-9a-fA-F-]{36})\|([^\]]+)\]")

logger = get_logger()


@dataclass
class Venue:
    mbid: str
    name: str
    city: str
    address: str | None = None

    def __hash__(self):
        return hash(self.mbid)


@dataclass
class Concert:
    mbid: str
    artist: str
    name: str
    year: int
    month: int
    day: int
    venue: str


@dataclass
class SetlistEntry:
    song_mbid: str
    concert_mbid: str
    position: int


def split_iso_loose(value: str):
    m = re.match(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", value)
    if not m:
        return None, None, None

    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) and 1 <= int(m.group(2)) <= 12 else None
    day = int(m.group(3)) if m.group(3) and 1 <= int(m.group(3)) <= 31 else None

    return year, month, day


def parse_mb_entity(text: str):
    m = MB_LINK_RE.search(text)
    if m:
        mbid = m.group(1)
        name = m.group(2)
        return mbid, name

    return None, text.strip()


def parse_setlist(songs: dict[tuple[str, str], str], artist_mbid: str, concert_mbid: str, setlist: str) -> list[SetlistEntry]:
    entries = []
    position = 1

    for line in setlist.splitlines():
        # strip the line
        line = line.strip()
        if not line:
            continue

        # make sure the setlist line is valid
        m = LINE_RE.match(line)
        if not m:
            continue

        # only look at songs
        prefix, content = m.groups()

        if prefix == "*":
            song_mbid, name = parse_mb_entity(content)
            if not song_mbid:
                song_mbid = songs.get((artist_mbid, name))
            if song_mbid:
                entries.append(SetlistEntry(song_mbid=song_mbid, concert_mbid=concert_mbid, position=position))
                position += 1

    return entries


def load_events(path: Path, songs: dict[tuple[str, str], str], artist_ids: set[str]) -> tuple[
    list[Concert], list[Venue], list[SetlistEntry]]:
    concerts = []
    venues = set()
    entries = []
    line_count, kept_count = 0, 0

    with open(path, "rb") as f:
        for line in f:
            line_count += 1

            if line_count % PROGRESS_INTERVAL == 0:
                logger.info(f"Read {line_count}, kept {kept_count} concerts")

            event = orjson.loads(line)

            # we only care about concerts
            if (event.get("type") or "").lower() != "concert":
                continue

            # and only where one of the artists is the main performer
            venue = None
            artist_id = None

            for relation in event.get("relations", []):
                relation_type = relation.get("type", "").lower()

                match relation_type:
                    case "held at":
                        place = relation.get("place", {})
                        mbid = place.get("id")
                        name = place.get("name")
                        city = (place.get("area") or {}).get("name")

                        address = place.get("address")
                        if address == "":
                            address = None

                        venue = Venue(mbid=mbid, name=name, city=city, address=address)
                    case "main performer":
                        current_id = relation.get("artist", {}).get("id")
                        if current_id in artist_ids:
                            artist_id = current_id

            if artist_id is not None:
                kept_count += 1

                mbid = event.get("id")
                title = event.get("name")
                date = event.get("life-span", {}).get("begin")
                if not date:
                    continue

                year, month, day = split_iso_loose(date)

                entries.extend(parse_setlist(songs, artist_id, mbid, event.get("setlist")))

                venue_id = None
                if venue is not None:
                    venue_id = venue.mbid
                    venues.add(venue)

                concert = Concert(mbid=mbid, artist=artist_id, name=title, year=year, month=month, day=day,
                                  venue=venue_id)
                concerts.append(concert)

    logger.info(f"Finished processing events.")
    return concerts, list(venues), entries
