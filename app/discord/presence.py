from __future__ import annotations

import os
from typing import Any, Optional

from .ipc import DiscordIPC


class DiscordPresence:
    def __init__(
        self,
        client_id: str,
    ) -> None:
        self.ipc = DiscordIPC(client_id)
        self.pid = os.getpid()

    @property
    def connected(self) -> bool:
        return self.ipc.connected

    def is_alive(self) -> bool:
        return self.ipc.is_alive()

    def connect(self) -> None:
        self.ipc.connect()

    def reconnect(self) -> None:
        self.ipc.reconnect()

    def close(self) -> None:
        self.ipc.close()

    def set_activity(
        self,
        *,
        details: Optional[str] = None,
        state: Optional[str] = None,
        start_timestamp: Optional[int] = None,
        large_image: Optional[str] = None,
        large_text: Optional[str] = None,
        small_image: Optional[str] = None,
        small_text: Optional[str] = None,
        buttons: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        activity: dict[str, Any] = {
            "type": 0,
        }

        if details:
            activity["details"] = details[:128]

        if state:
            activity["state"] = state[:128]

        if start_timestamp:
            activity["timestamps"] = {
                "start": start_timestamp,
            }

        assets: dict[str, str] = {}

        if large_image:
            assets["large_image"] = large_image

        if large_text:
            assets["large_text"] = large_text

        if small_image:
            assets["small_image"] = small_image

        if small_text:
            assets["small_text"] = small_text

        if assets:
            activity["assets"] = assets

        if buttons:
            activity["buttons"] = buttons[:2]

        return self.ipc.send_command(
            "SET_ACTIVITY",
            {
                "pid": self.pid,
                "activity": activity,
            },
        )

    def clear(self) -> dict[str, Any]:
        return self.ipc.send_command(
            "SET_ACTIVITY",
            {
                "pid": self.pid,
                "activity": None,
            },
        )