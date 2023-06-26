import urllib
from os import environ
from typing import Any, Dict, Optional, Self

import httpx
from httpx import Response
from loguru import logger


class TMDB:
    """Class to integrate with the TMDB API."""

    def FetchData(
        self: Self, apiKey: str, lTitle: str, lType: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch data for the specified title and media type from the TMDB API."""

        data: Dict[str, Any] = {}

        try:
            res: Response = httpx.get(
                f"https://api.themoviedb.org/3/search/multi?api_key={apiKey}&query={urllib.parse.quote(lTitle)}"
            )

            res.raise_for_status()

            logger.trace(res.text)

            data = res.json()
        except Exception as e:
            logger.error(f"Failed to fetch data for {lType} {lTitle} from TMDB, {e}")

            return

        for entry in data.get("results", []):
            rTitle: str = entry.get("name") or entry.get("title")
            rType: str = entry.get("media_type")

            # Change local type to match TMDB
            if lType == "episode":
                lType = "tv"

            if lTitle.lower() != rTitle.lower():
                continue
            elif lType != rType:
                continue

            return entry

    def Thumbnail(self: Self, lTitle: str, lType: str) -> Optional[str]:
        """
        Return a thumbnail image URL for the specified title and media type.
        """

        if not (key := environ.get("TMDB_API_KEY")):
            logger.info("Failed to fetch media thumbnail, TMDB API Key is not set")

            return

        data: Optional[Dict[str, Any]] = TMDB.FetchData(self, key, lTitle, lType)

        if data:
            rPoster: str = data.get("poster_path")

            if rPoster:
                return f"https://image.tmdb.org/t/p/original{rPoster}"

        logger.info(f"Unable to locate thumbnail for {lType} {lTitle} on TMDB")

    def Info(self: Self, lTitle: str, lType: str) -> Optional[str]:
        """Return the TMDB URL for the specified title and media type."""

        if not (key := environ.get("TMDB_API_KEY")):
            logger.info("Failed to fetch media information, TMDB API Key is not set")

            return

        data: Optional[Dict[str, Any]] = TMDB.FetchData(self, key, lTitle, lType)

        if data:
            rType: str = data.get("media_type")
            rID: int = data.get("id")

            if rID:
                return f"https://www.themoviedb.org/{rType}/{rID}"

        logger.info(f"Unable to locate media information for {lType} {lTitle} on TMDB")
