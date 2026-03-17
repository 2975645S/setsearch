from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from requests import Session

from data.wrangler.songs import CoverArtRef
from data.wrangler.util import get_logger

MAX_WORKERS = 16
PROGRESS_INTERVAL = 100

logger = get_logger()

def fetch_cover_by_release(http: Session, release: str, refs: list[CoverArtRef]):
    res = http.get(f"https://coverartarchive.org/release/{release}", timeout=10)
    image = None

    if res.status_code == 200:
        data = res.json()
        image = data.get("images", [{}])[0].get("image")

    if image is None:
        group = refs[0].release_group
        if group:
            res = http.get(f"https://coverartarchive.org/release-group/{group}", timeout=10)
            if res.status_code == 200:
                data = res.json()
                image = data.get("images", [{}])[0].get("image")

    return refs, image

def fetch_all_covers(http: Session, refs: list[CoverArtRef]) -> dict[str, str | None]:
    covers: dict[str, str | None] = {}
    release_map: dict[str, list[CoverArtRef]] = defaultdict(list)
    futures = []

    for ref in refs:
        if ref.release:
            release_map[ref.release].append(ref)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i, (release, rrefs) in enumerate(release_map.items()):
            futures.append(pool.submit(fetch_cover_by_release, http, release, rrefs))

            if i % PROGRESS_INTERVAL == 0:
                logger.info(f"Submitted cover fetch for {i}/{len(release_map)} releases")

        processed = 0
        for i, f in enumerate(futures):
            rrefs, image = f.result()

            for ref in rrefs:
                covers[ref.song] = image
                processed += 1

            if i % PROGRESS_INTERVAL == 0:
                logger.info(f"Fetched covers for {processed}/{len(release_map)} releases")

    logger.info("Finished fetching covers")
    return covers
