import re
from typing import Optional
from urllib.parse import urlparse
import requests
from app.kick.models import KickLivestream


class KickClient:
    def __init__(self, kick_url: str):
        self.kick_url = kick_url
        self.channel_name = self.extract_channel_name(kick_url)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
            }
        )

    def update_url(self, kick_url: str):
        self.kick_url = kick_url
        self.channel_name = self.extract_channel_name(kick_url)

    @staticmethod
    def extract_channel_name(url_or_name: str) -> str:
        value = url_or_name.strip()
        if not value:
            raise ValueError("Kick URL veya kanal adı boş olamaz.")

        if not value.startswith("http://") and not value.startswith("https://"):
            value = "https://" + value

        try:
            parsed = urlparse(value)
            path = parsed.path.strip("/")
            if not path:
                raise ValueError("Kick kanal adı URL içinden çıkarılamadı.")
            channel = path.split("/")[0].strip()
            if not channel:
                raise ValueError("Kick kanal adı geçersiz.")
            channel = re.sub(r"[^a-zA-Z0-9_\-]", "", channel)
            if not channel:
                raise ValueError("Kick kanal adı geçersiz karakterler içeriyor.")
            return channel
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Geçersiz Kick URL: {e}")

    def get_channel_url(self) -> str:
        return f"https://kick.com/{self.channel_name}"

    def get_livestream_status(self) -> KickLivestream:
        url = f"https://kick.com/api/v2/channels/{self.channel_name}"
        try:
            response = self.session.get(url, timeout=10)
        except requests.RequestException as e:
            raise ConnectionError(f"Kick sunucusuna bağlanılamadı: {e}")

        if response.status_code == 404:
            raise ValueError(f"Kick kanalı bulunamadı: {self.channel_name}")

        if response.status_code != 200:
            return KickLivestream(
                is_live=False,
                channel_name=self.channel_name,
                channel_url=self.get_channel_url(),
            )

        try:
            data = response.json()
        except ValueError:
            raise ValueError("Kick API geçerli bir JSON yanıtı döndürmedi.")

        livestream = data.get("livestream")
        if not livestream or not livestream.get("is_live", False):
            return KickLivestream(
                is_live=False,
                channel_name=self.channel_name,
                channel_url=self.get_channel_url(),
            )

        categories = livestream.get("categories", [])
        category_name = None
        if categories and isinstance(categories, list):
            first_cat = categories[0]
            if isinstance(first_cat, dict):
                category_name = first_cat.get("name")

        thumbnail = livestream.get("thumbnail")
        thumbnail_url = None
        if isinstance(thumbnail, dict):
            thumbnail_url = thumbnail.get("url")
        elif isinstance(thumbnail, str):
            thumbnail_url = thumbnail

        return KickLivestream(
            is_live=True,
            session_title=livestream.get("session_title") or "Yayın Başlığı Yok",
            category_name=category_name or "Just Chatting",
            viewer_count=int(livestream.get("viewer_count", 0)),
            start_time=livestream.get("start_time"),
            thumbnail_url=thumbnail_url,
            channel_name=self.channel_name,
            channel_url=self.get_channel_url(),
        )
