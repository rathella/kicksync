import json
import os
from typing import Any, Dict


class AppState:
    DEFAULT_CONFIG = {
        "kick_url": "https://kick.com/rathellaizm",
        "discord_client_id": "1547766245993226380",
        "poll_interval": 5,
        "start_with_windows": False,
        "minimize_to_tray": False,
        "language": "Türkçe",
        "theme": "Dark",
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except Exception:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save()
