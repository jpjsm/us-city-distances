# Source: https://copilot.microsoft.com/shares/3Z2QCcdYrWfBvPXSLhah9
import os
import time
import uuid
import shutil
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter, Retry

from config import GEOFABRIK_FOLDER
from geofabrik_constants import OSM_PBF_US_STATES_TERRITORIES_URLS


def make_session():
    """Create a requests.Session with retry logic and connection pooling."""
    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(
        max_retries=retries,
        pool_connections=100,
        pool_maxsize=100,
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download_one(url: str, dest_folder: Path, session: requests.Session):
    """Download a single PBF file with streaming and retries."""
    filename = url.rstrip("/").split("/")[-1]
    if not filename.endswith(".pbf"):
        filename = f"{filename}_{uuid.uuid4().hex}.pbf"

    tmp_path = dest_folder / f".{filename}.part"
    final_path = dest_folder / filename

    try:
        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        shutil.move(tmp_path, final_path)
        return final_path

    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise RuntimeError(f"Failed to download {url}: {e}") from e


def download_all(urls, dest_folder, threads=8):
    """Download many PBF files concurrently."""
    dest = Path(dest_folder)
    dest.mkdir(parents=True, exist_ok=True)

    session = make_session()

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = {pool.submit(download_one, url, dest, session): url for url in urls}

        for future in as_completed(futures):
            url = futures[future]
            try:
                path = future.result()
                logging.info(f"Downloaded: {url} → {path}")
            except Exception as e:
                logging.error(str(e))


if __name__ == "__main__":
    download_all(OSM_PBF_US_STATES_TERRITORIES_URLS, GEOFABRIK_FOLDER, threads=8)
