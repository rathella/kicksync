from dataclasses import dataclass
from typing import Optional


@dataclass
class KickLivestream:
    is_live: bool
    session_title: Optional[str] = None
    category_name: Optional[str] = None
    viewer_count: int = 0
    start_time: Optional[str] = None
    thumbnail_url: Optional[str] = None
    channel_name: Optional[str] = None
    channel_url: Optional[str] = None
