from __future__ import annotations

import time
from dataclasses import dataclass


INITIAL_RECONNECT_DELAY = 1
MAX_RECONNECT_DELAY = 30


@dataclass
class ConnectionState:
    connected: bool = False
    reconnect_delay: int = INITIAL_RECONNECT_DELAY
    next_reconnect_at: float = 0.0

    def mark_connected(self) -> None:
        self.connected = True
        self.reconnect_delay = INITIAL_RECONNECT_DELAY
        self.next_reconnect_at = 0.0

    def mark_disconnected(self) -> None:
        self.connected = False
        self.next_reconnect_at = (
            time.monotonic() + self.reconnect_delay
        )

    def can_reconnect(self) -> bool:
        if self.connected:
            return False

        return time.monotonic() >= self.next_reconnect_at

    def increase_backoff(self) -> None:
        self.reconnect_delay = min(
            self.reconnect_delay * 2,
            MAX_RECONNECT_DELAY,
        )