from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import requests

from .models import KickStream


class KickError(Exception):
    """Kick API ile ilgili hatalar."""


class KickClient:
    BASE_URL = "https://kick.com/api/v2/channels"

    def __init__(
        self,
        kick_url: str,
        timeout: float = 10.0,
    ) -> None:
        self.kick_url = kick_url.strip()
        self.timeout = timeout

        self.username = self._extract_username(
            self.kick_url
        )

    @staticmethod
    def _extract_username(kick_url: str) -> str:
        parsed = urlparse(kick_url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                "Kick linki http:// veya https:// ile başlamalı."
            )

        if parsed.netloc.lower() not in (
            "kick.com",
            "www.kick.com",
        ):
            raise ValueError(
                "Geçerli bir Kick kanal linki gir."
            )

        parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if not parts:
            raise ValueError(
                "Kick kanal linkinde kullanıcı adı bulunamadı."
            )

        username = parts[0].strip()

        if not username:
            raise ValueError(
                "Kick kullanıcı adı boş olamaz."
            )

        return username

    def fetch(self) -> KickStream:
        url = f"{self.BASE_URL}/{self.username}"

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "KickSync/1.0",
                },
            )
        except requests.RequestException as exc:
            raise KickError(
                f"Kick API bağlantı hatası: {exc}"
            ) from exc

        if response.status_code == 404:
            raise KickError(
                f"Kick kullanıcısı bulunamadı: {self.username}"
            )

        if response.status_code != 200:
            raise KickError(
                f"Kick API HTTP {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise KickError(
                "Kick API geçersiz JSON döndürdü."
            ) from exc

        return self._parse_channel(data)

    def _parse_channel(
        self,
        data: dict[str, Any],
    ) -> KickStream:
        livestream = data.get("livestream")

        if not livestream or not livestream.get("is_live"):
            return KickStream(
                is_live=False,
                username=self.username,
            )

        categories = livestream.get(
            "categories"
        ) or []

        category: Optional[str] = None

        if categories:
            first_category = categories[0]

            if isinstance(first_category, dict):
                category = first_category.get("name")

        started_at = self._parse_datetime(
            livestream.get("start_time")
        )

        thumbnail_url = self._extract_thumbnail_url(
            livestream.get("thumbnail")
        )

        return KickStream(
            is_live=True,
            username=self.username,
            title=livestream.get("session_title"),
            category=category,
            viewers=int(
                livestream.get("viewer_count") or 0
            ),
            started_at=started_at,
            thumbnail_url=thumbnail_url,
        )

    @staticmethod
    def _extract_thumbnail_url(
        thumbnail: Any,
    ) -> Optional[str]:
        if isinstance(thumbnail, str):
            return thumbnail.strip() or None

        if isinstance(thumbnail, dict):
            url = thumbnail.get("url")

            if isinstance(url, str):
                return url.strip() or None

        return None

    @staticmethod
    def _parse_datetime(
        value: Optional[str],
    ) -> Optional[datetime]:
        if not value:
            return None

        formats = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        )

        for fmt in formats:
            try:
                parsed = datetime.strptime(
                    value,
                    fmt,
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=timezone.utc
                    )

                return parsed

            except ValueError:
                continue

        return None