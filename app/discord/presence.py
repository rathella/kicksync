from datetime import datetime
from typing import Optional
from app.discord.ipc import DiscordIPC
from app.kick.models import KickLivestream


class DiscordPresenceManager:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ipc = DiscordIPC(client_id)
        self.last_livestream: Optional[KickLivestream] = None

    def update_client_id(self, client_id: str):
        if self.client_id != client_id:
            self.client_id = client_id
            self.ipc.disconnect()
            self.ipc = DiscordIPC(client_id)

    @property
    def is_connected(self) -> bool:
        return self.ipc.is_connected

    def connect(self) -> bool:
        return self.ipc.connect()

    def disconnect(self):
        self.ipc.disconnect()

    @staticmethod
    def _parse_timestamp(iso_str: Optional[str]) -> Optional[int]:
        if not iso_str:
            return None
        try:
            clean_str = iso_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            return int(dt.timestamp())
        except (ValueError, TypeError):
            return None

    def update_presence(self, livestream: KickLivestream) -> bool:
        self.last_livestream = livestream

        if not livestream.is_live:
            return self.ipc.clear_activity()

        start_timestamp = self._parse_timestamp(livestream.start_time)

        details = livestream.session_title or "Canlı Yayın"
        if len(details) > 128:
            details = details[:125] + "..."

        category = livestream.category_name or "Just Chatting"
        viewers = livestream.viewer_count
        state = f"{category} • {viewers:,} izleyici"
        if len(state) > 128:
            state = state[:128]

        activity = {
            "type": 0,
            "details": details,
            "state": state,
            "assets": {
                "large_image": "kick_logo",
                "large_text": livestream.session_title or "Kick Stream",
                "small_image": "kick_verified",
                "small_text": f"kick.com/{livestream.channel_name}",
            },
        }

        if start_timestamp:
            activity["timestamps"] = {"start": start_timestamp}

        channel_url = livestream.channel_url or "https://kick.com"
        activity["buttons"] = [
            {"label": "Yayını İzle", "url": channel_url}
        ]

        return self.ipc.send_activity(activity)

    def clear(self) -> bool:
        return self.ipc.clear_activity()
