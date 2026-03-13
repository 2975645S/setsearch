import re
from dataclasses import dataclass
from pathlib import Path

import orjson

from data.wrangler.util import get_logger

PROGRESS_INTERVAL = 100

logger = get_logger()

@dataclass
class Concert:
    artist: str
    title: str
    year: int
    month: int
    day: int
    venue: str

def split_iso_loose(value: str):
    m = re.match(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", value)
    if not m:
        return None, None, None

    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) and 1 <= int(m.group(2)) <= 12 else None
    day = int(m.group(3)) if m.group(3) and 1 <= int(m.group(3)) <= 31 else None

    return year, month, day

def load_events(path: Path, artist_ids: set[str]) -> list[Concert]:
    concerts = []
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
                        venue = relation.get("place", {}).get("name")
                    case "main performer":
                        current_id = relation.get("artist", {}).get("id")
                        if current_id in artist_ids:
                            artist_id = current_id

            if artist_id is not None:
                kept_count += 1

                title = event.get("name")
                date = event.get("life-span", {}).get("begin")
                year, month, day = split_iso_loose(date)

                concert = Concert(artist=artist_id, title=title, year=year, month=month, day=day, venue=venue)
                concerts.append(concert)

    logger.info(f"Finished processing events.")
    return concerts