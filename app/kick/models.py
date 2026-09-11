from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class KickStream:
    is_live: bool
    username: str

    title: Optional[str] = None
    category: Optional[str] = None
    viewers: int = 0

    started_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None

    @property
    def url(self) -> str:
        return f"https://kick.com/{self.username}"