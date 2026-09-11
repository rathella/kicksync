from __future__ import annotations

import json
import threading
import time
import webbrowser
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Optional

import customtkinter as ctk
import requests
from PIL import Image, ImageTk

from app.discord.ipc import DiscordIPCError
from app.discord.presence import DiscordPresence
from app.kick.client import KickClient, KickError
from app.kick.models import KickStream
from app.state import ConnectionState
from app.ui.settings_window import SettingsWindow


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_POLL_INTERVAL = 5

ACCENT = "#53FC18"
ACCENT_HOVER = "#68FF35"
ACCENT_PRESSED = "#45DB12"

DARK_BG = "#18181B"
DARK_CARD = "#202024"
DARK_CARD_ALT = "#1B1B1F"
DARK_BORDER = "#303034"
DARK_BORDER_HOVER = "#45454B"

TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#A1A1AA"
TEXT_MUTED = "#71717A"

ERROR = "#FF5C68"


class ThumbnailLoader:
    """Thumbnail'ı UI thread'ini bloklamadan indirir."""

    def __init__(
        self,
        url: str,
        callback: Callable[[bytes], None],
        error_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        self.url = url
        self.callback = callback
        self.error_callback = error_callback

    def start(self) -> None:
        thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        thread.start()

    def _run(self) -> None:
        try:
            response = requests.get(
                self.url,
                timeout=10,
                headers={
                    "User-Agent": "KickSync/1.0",
                },
            )

            response.raise_for_status()
            self.callback(response.content)

        except requests.RequestException:
            if self.error_callback is not None:
                self.error_callback()


class StatCard(ctk.CTkFrame):
    """İzleyici ve süre istatistik kartı."""

    def __init__(
        self,
        master: Any,
        label: str,
        value: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=DARK_CARD_ALT,
            border_width=1,
            border_color=DARK_BORDER,
            corner_radius=10,
            height=58,
            **kwargs,
        )

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=label,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
                weight="bold",
            ),
            anchor="w",
        )

        self.label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=(7, 0),
        )

        self.value = ctk.CTkLabel(
            self,
            text=value,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
                weight="bold",
            ),
            anchor="w",
        )

        self.value.grid(
            row=1,
            column=0,
            sticky="w",
            padx=12,
            pady=(0, 7),
        )

    def set_value(self, value: str) -> None:
        self.value.configure(text=value)


class StatusBadge(ctk.CTkFrame):
    """LIVE/OFFLINE durum rozeti."""

    def __init__(
        self,
        master: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color="#292024",
            corner_radius=10,
            height=27,
            **kwargs,
        )

        self.dot = ctk.CTkLabel(
            self,
            text="●",
            text_color="#FF707B",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
                weight="bold",
            ),
            width=8,
        )

        self.dot.pack(
            side="left",
            padx=(10, 3),
        )

        self.label = ctk.CTkLabel(
            self,
            text="OFFLINE",
            text_color="#FF707B",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
                weight="bold",
            ),
        )

        self.label.pack(
            side="left",
            padx=(0, 10),
        )

    def set_status(self, live: bool) -> None:
        if live:
            self.configure(
                fg_color="#17310F",
            )

            self.dot.configure(
                text_color=ACCENT,
            )

            self.label.configure(
                text="LIVE",
                text_color=ACCENT,
            )

        else:
            self.configure(
                fg_color="#292024",
            )

            self.dot.configure(
                text_color="#FF707B",
            )

            self.label.configure(
                text="OFFLINE",
                text_color="#FF707B",
            )


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("KickSync")
        self.geometry("500x700")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.discord: Optional[DiscordPresence] = None
        self.kick: Optional[KickClient] = None

        self.connection = ConnectionState()
        self.previous_stream: Optional[KickStream] = None

        self.poll_interval = DEFAULT_POLL_INTERVAL
        self.theme = "Dark"

        self.thumbnail_image: Optional[ImageTk.PhotoImage] = None
        self.thumbnail_request_id = 0

        self._build_ui()
        self._load_config()
        self._connect_discord()

        self.after(
            self.poll_interval * 1000,
            self._poll_loop,
        )

        self.update_data()

        self.protocol(
            "WM_DELETE_WINDOW",
            self._on_close,
        )

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self) -> None:
        self.configure(
            fg_color=DARK_BG,
        )

        self.main = ctk.CTkFrame(
            self,
            fg_color=DARK_BG,
            corner_radius=0,
        )

        self.main.pack(
            fill="both",
            expand=True,
        )

        self.main.grid_columnconfigure(
            0,
            weight=1,
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = ctk.CTkFrame(
            self.main,
            fg_color="transparent",
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=24,
            pady=(18, 0),
        )

        header.grid_columnconfigure(
            0,
            weight=1,
        )

        brand = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        brand.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.title_label = ctk.CTkLabel(
            brand,
            text="KickSync",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=26,
                weight="bold",
            ),
        )

        self.title_label.pack(
            anchor="w",
        )

        self.subtitle_label = ctk.CTkLabel(
            brand,
            text="Kick → Discord Rich Presence",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
            ),
        )

        self.subtitle_label.pack(
            anchor="w",
            pady=(0, 1),
        )

        self.live_status = StatusBadge(
            header,
        )

        self.live_status.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(12, 0),
            pady=(2, 0),
        )

        # -----------------------------------------------------
        # USERNAME
        # -----------------------------------------------------

        self.username = ctk.CTkLabel(
            self.main,
            text="@kullanici",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
            anchor="w",
        )

        self.username.grid(
            row=1,
            column=0,
            sticky="w",
            padx=24,
            pady=(2, 7),
        )

        # -----------------------------------------------------
        # STREAM CARD
        # -----------------------------------------------------

        self.stream_card = ctk.CTkFrame(
            self.main,
            fg_color=DARK_CARD,
            border_width=1,
            border_color=DARK_BORDER,
            corner_radius=15,
        )

        self.stream_card.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=24,
        )

        self.stream_card.grid_columnconfigure(
            0,
            weight=1,
        )

        # Thumbnail
        self.thumbnail_frame = ctk.CTkFrame(
            self.stream_card,
            fg_color="#111113",
            corner_radius=13,
            height=215,
        )

        self.thumbnail_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=1,
            pady=1,
        )

        self.thumbnail_frame.grid_propagate(False)

        self.thumbnail = ctk.CTkLabel(
            self.thumbnail_frame,
            text="KICK\n\nYayın kapalı",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold",
            ),
            justify="center",
        )

        self.thumbnail.pack(
            fill="both",
            expand=True,
        )

        # Content
        content = ctk.CTkFrame(
            self.stream_card,
            fg_color="transparent",
        )

        content.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(9, 14),
        )

        content.grid_columnconfigure(
            0,
            weight=1,
        )

        stream_label = ctk.CTkLabel(
            content,
            text="YAYIN",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
                weight="bold",
            ),
            anchor="w",
        )

        stream_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.stream_title = ctk.CTkLabel(
            content,
            text="Yayın şu anda kapalı.",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold",
            ),
            anchor="w",
            justify="left",
            wraplength=410,
        )

        self.stream_title.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

        self.category = ctk.CTkLabel(
            content,
            text="Kanal şu anda canlı değil.",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
            anchor="w",
        )

        self.category.grid(
            row=2,
            column=0,
            sticky="w",
            pady=(1, 0),
        )

        stats = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )

        stats.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(8, 0),
        )

        stats.grid_columnconfigure(
            0,
            weight=1,
        )

        stats.grid_columnconfigure(
            1,
            weight=1,
        )

        self.viewers_card = StatCard(
            stats,
            "İZLEYİCİ",
            "0",
        )

        self.viewers_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 3),
        )

        self.elapsed_card = StatCard(
            stats,
            "SÜRE",
            "--:--:--",
        )

        self.elapsed_card.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(3, 0),
        )

        # -----------------------------------------------------
        # PRIMARY BUTTON
        # -----------------------------------------------------

        self.open_button = ctk.CTkButton(
            self.main,
            text="Yayını Aç",
            height=38,
            corner_radius=19,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#101510",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
            command=self._open_kick_stream,
            state="disabled",
        )

        self.open_button.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=24,
            pady=(9, 0),
        )

        # -----------------------------------------------------
        # SECONDARY BUTTONS
        # -----------------------------------------------------

        secondary = ctk.CTkFrame(
            self.main,
            fg_color="transparent",
        )

        secondary.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=24,
            pady=(7, 0),
        )

        secondary.grid_columnconfigure(
            0,
            weight=1,
        )

        secondary.grid_columnconfigure(
            1,
            weight=1,
        )

        self.refresh_button = ctk.CTkButton(
            secondary,
            text="↻  Şimdi Yenile",
            height=36,
            corner_radius=9,
            fg_color=DARK_CARD_ALT,
            hover_color="#29292E",
            border_width=1,
            border_color=DARK_BORDER,
            text_color="#C4C4CA",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            command=self._manual_refresh,
        )

        self.refresh_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )

        self.settings_button = ctk.CTkButton(
            secondary,
            text="⚙  Settings",
            height=36,
            corner_radius=9,
            fg_color=DARK_CARD_ALT,
            hover_color="#29292E",
            border_width=1,
            border_color=DARK_BORDER,
            text_color="#C4C4CA",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            command=self._open_settings,
        )

        self.settings_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(4, 0),
        )

        # -----------------------------------------------------
        # LAST UPDATE
        # -----------------------------------------------------

        self.last_update = ctk.CTkLabel(
            self.main,
            text="Son kontrol: --:--:--",
            text_color="#5F5F67",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=8,
            ),
        )

        self.last_update.grid(
            row=5,
            column=0,
            pady=(6, 6),
        )

        # -----------------------------------------------------
        # DISCORD CARD
        # -----------------------------------------------------

        self.discord_card = ctk.CTkFrame(
            self.main,
            fg_color=DARK_CARD_ALT,
            border_width=1,
            border_color=DARK_BORDER,
            corner_radius=11,
            height=55,
        )

        self.discord_card.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 17),
        )

        self.discord_card.grid_propagate(False)

        self.discord_card.grid_columnconfigure(
            1,
            weight=1,
        )

        # Tek status dot.
        self.discord_icon = ctk.CTkLabel(
            self.discord_card,
            text="●",
            text_color=ACCENT,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            width=12,
        )

        self.discord_icon.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(14, 7),
            pady=0,
        )

        # Başlık + durum aynı yatay hiyerarşide.
        discord_text = ctk.CTkFrame(
            self.discord_card,
            fg_color="transparent",
        )

        discord_text.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 12),
        )

        self.discord_title = ctk.CTkLabel(
            discord_text,
            text="Discord Rich Presence",
            text_color="#E4E4E7",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            anchor="w",
        )

        self.discord_title.pack(
            side="left",
            padx=(0, 8),
        )

        self.discord_status = ctk.CTkLabel(
            discord_text,
            text="Connected",
            text_color=ACCENT,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=9,
                weight="bold",
            ),
            anchor="w",
        )

        self.discord_status.pack(
            side="left",
        )

    # =========================================================
    # CONFIG
    # =========================================================

    def _load_config(self) -> None:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"Config dosyası bulunamadı: {CONFIG_PATH}"
            )

        try:
            with CONFIG_PATH.open(
                "r",
                encoding="utf-8",
            ) as file:
                config = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "config.json geçersiz JSON içeriyor."
            ) from exc

        discord_client_id = str(
            config["discord_client_id"]
        )

        kick_url = str(
            config["kick_url"]
        )

        self.poll_interval = int(
            config.get(
                "poll_interval",
                DEFAULT_POLL_INTERVAL,
            )
        )

        if self.poll_interval < 1:
            self.poll_interval = DEFAULT_POLL_INTERVAL

        self.theme = str(
            config.get(
                "theme",
                "Dark",
            )
        )

        if self.theme not in (
            "Dark",
            "Light",
            "System",
        ):
            self.theme = "Dark"

        self.kick = KickClient(
            kick_url,
        )

        self.discord = DiscordPresence(
            discord_client_id,
        )

        self.username.configure(
            text=f"@{self.kick.username}",
        )

        self._apply_theme()

    # =========================================================
    # THEME
    # =========================================================

    def _apply_theme(self) -> None:
        if self.theme == "Light":
            ctk.set_appearance_mode("light")
        elif self.theme == "System":
            ctk.set_appearance_mode("system")
        else:
            ctk.set_appearance_mode("dark")

    # =========================================================
    # DISCORD
    # =========================================================

    def _connect_discord(self) -> None:
        if self.discord is None:
            return

        try:
            self.discord.connect()
            self.connection.mark_connected()
            self._set_discord_status("connected")

        except DiscordIPCError:
            self.connection.mark_disconnected()
            self._set_discord_status("disconnected")

    def _refresh_discord_connection(self) -> None:
        if self.discord is None:
            return

        if self.connection.connected:
            if not self.discord.is_alive():
                self.connection.mark_disconnected()
                self._set_discord_status("disconnected")

            return

        self._try_reconnect()

    def _try_reconnect(self) -> None:
        if self.discord is None:
            return

        if not self.connection.can_reconnect():
            return

        try:
            self.discord.reconnect()

        except DiscordIPCError:
            self.connection.mark_disconnected()
            self._set_discord_status("disconnected")
            self.connection.increase_backoff()
            return

        self.connection.mark_connected()
        self._set_discord_status("connected")

    def _set_discord_status(
        self,
        status: str,
    ) -> None:
        if status == "connected":
            self.discord_icon.configure(
                text_color=ACCENT,
            )

            self.discord_status.configure(
                text="Connected",
                text_color=ACCENT,
            )

        elif status == "disconnected":
            self.discord_icon.configure(
                text_color=ERROR,
            )

            self.discord_status.configure(
                text="Disconnected",
                text_color=ERROR,
            )

        else:
            self.discord_icon.configure(
                text_color=TEXT_MUTED,
            )

            self.discord_status.configure(
                text="Connecting...",
                text_color=TEXT_SECONDARY,
            )

    # =========================================================
    # KICK POLLING
    # =========================================================

    def _poll_loop(self) -> None:
        self.update_data()

        self.after(
            self.poll_interval * 1000,
            self._poll_loop,
        )

    def update_data(self) -> None:
        if self.kick is None:
            return

        self._refresh_discord_connection()

        try:
            stream = self.kick.fetch()

        except KickError as exc:
            self.stream_title.configure(
                text="Kick bağlantı hatası",
            )

            self.category.configure(
                text=str(exc),
            )

            self.open_button.configure(
                state="disabled",
            )

            self._update_last_check()
            return

        was_live = (
            self.previous_stream is not None
            and self.previous_stream.is_live
        )

        if stream.is_live:
            self._update_live_state(stream)

        else:
            self._update_offline_state(was_live)

        self.previous_stream = stream
        self._update_last_check()

    # =========================================================
    # LIVE
    # =========================================================

    def _update_live_state(
        self,
        stream: KickStream,
    ) -> None:
        self.live_status.set_status(True)

        self.stream_title.configure(
            text=stream.title
            or "Kick'te canlı yayın",
        )

        self.category.configure(
            text=stream.category
            or "Kategori bilinmiyor",
        )

        self.viewers_card.set_value(
            f"{stream.viewers:,}",
        )

        self.open_button.configure(
            state="normal",
        )

        if stream.started_at:
            elapsed_seconds = max(
                0,
                int(
                    time.time()
                    - stream.started_at.timestamp()
                ),
            )

            self.elapsed_card.set_value(
                self._format_elapsed(
                    elapsed_seconds,
                ),
            )

        else:
            self.elapsed_card.set_value(
                "--:--:--",
            )

        if stream.thumbnail_url:
            self._load_thumbnail(
                stream.thumbnail_url,
            )

        else:
            self._show_thumbnail_placeholder(
                "KICK\n\nCanlı yayın",
            )

        if self.connection.connected:
            self._update_discord_presence(
                stream,
            )

    # =========================================================
    # OFFLINE
    # =========================================================

    def _update_offline_state(
        self,
        was_live: bool,
    ) -> None:
        self.live_status.set_status(False)

        self.stream_title.configure(
            text="Yayın şu anda kapalı.",
        )

        self.category.configure(
            text="Kanal şu anda canlı değil.",
        )

        self.viewers_card.set_value("0")

        self.elapsed_card.set_value(
            "--:--:--",
        )

        self.open_button.configure(
            state="disabled",
        )

        self._show_thumbnail_placeholder(
            "KICK\n\nYayın kapalı",
        )

        if was_live:
            self._clear_discord_presence()

    # =========================================================
    # THUMBNAIL
    # =========================================================

    def _load_thumbnail(
        self,
        url: str,
    ) -> None:
        self.thumbnail_request_id += 1

        request_id = self.thumbnail_request_id

        loader = ThumbnailLoader(
            url,
            callback=lambda data: self.after(
                0,
                lambda: self._set_thumbnail(
                    data,
                    request_id,
                ),
            ),
            error_callback=lambda: None,
        )

        loader.start()

    def _set_thumbnail(
        self,
        data: bytes,
        request_id: int,
    ) -> None:
        if request_id != self.thumbnail_request_id:
            return

        try:
            image = Image.open(
                BytesIO(data),
            )

            width = max(
                self.thumbnail_frame.winfo_width(),
                1,
            )

            height = 215

            image = self._crop_image(
                image,
                width,
                height,
            )

            self.thumbnail_image = ImageTk.PhotoImage(
                image,
            )

            self.thumbnail.configure(
                image=self.thumbnail_image,
                text="",
            )

        except Exception:
            self._show_thumbnail_placeholder(
                "KICK\n\nCanlı yayın",
            )

    @staticmethod
    def _crop_image(
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        image = image.convert("RGB")

        source_width, source_height = image.size

        source_ratio = (
            source_width / source_height
        )

        target_ratio = (
            target_width / target_height
        )

        if source_ratio > target_ratio:
            new_height = target_height

            new_width = int(
                new_height * source_ratio,
            )

        else:
            new_width = target_width

            new_height = int(
                new_width / source_ratio,
            )

        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

        left = (
            new_width - target_width
        ) // 2

        top = (
            new_height - target_height
        ) // 2

        return image.crop(
            (
                left,
                top,
                left + target_width,
                top + target_height,
            )
        )

    def _show_thumbnail_placeholder(
        self,
        text: str,
    ) -> None:
        self.thumbnail_image = None

        self.thumbnail.configure(
            image=None,
            text=text,
        )

    # =========================================================
    # ACTIONS
    # =========================================================

    def _manual_refresh(self) -> None:
        self.refresh_button.configure(
            state="disabled",
            text="↻  Yenileniyor...",
        )

        try:
            self.update_data()

        finally:
            self.refresh_button.configure(
                state="normal",
                text="↻  Şimdi Yenile",
            )

    def _open_kick_stream(self) -> None:
        if self.kick is None:
            return

        webbrowser.open(
            f"https://kick.com/{self.kick.username}",
        )

    def _open_settings(self) -> None:
        settings_window = SettingsWindow(
            self,
            on_saved=self._settings_saved,
        )

        settings_window.grab_set()

    def _settings_saved(self) -> None:
        if self.discord is not None:
            self.discord.close()

        self._load_config()

        self.connection = ConnectionState()

        self._connect_discord()
        self.update_data()

    # =========================================================
    # DISCORD PRESENCE
    # =========================================================

    def _update_discord_presence(
        self,
        stream: KickStream,
    ) -> None:
        if self.discord is None:
            return

        start_timestamp: Optional[int] = None

        if stream.started_at:
            start_timestamp = int(
                stream.started_at.timestamp()
            )

        state = (
            f"{stream.viewers:,} izleyici"
        )

        if stream.category:
            state += (
                f" • {stream.category}"
            )

        try:
            self.discord.set_activity(
                details=(
                    stream.title
                    or "Kick'te canlı yayın"
                ),
                state=state,
                start_timestamp=start_timestamp,
                large_image="kick",
                large_text="Kick'te canlı",
                buttons=[
                    {
                        "label": "Yayını İzle",
                        "url": stream.url,
                    }
                ],
            )

            self.connection.mark_connected()

            self._set_discord_status(
                "connected",
            )

        except DiscordIPCError:
            self.discord.close()

            self.connection.mark_disconnected()
            self.connection.increase_backoff()

            self._set_discord_status(
                "disconnected",
            )

    def _clear_discord_presence(self) -> None:
        if self.discord is None:
            return

        if not self.connection.connected:
            return

        try:
            self.discord.clear()

        except DiscordIPCError:
            self.discord.close()

            self.connection.mark_disconnected()
            self.connection.increase_backoff()

            self._set_discord_status(
                "disconnected",
            )

    # =========================================================
    # HELPERS
    # =========================================================

    def _update_last_check(self) -> None:
        current_time = datetime.now().strftime(
            "%H:%M:%S",
        )

        self.last_update.configure(
            text=f"Son kontrol: {current_time}",
        )

    @staticmethod
    def _format_elapsed(
        seconds: int,
    ) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining = seconds % 60

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{remaining:02d}"
        )

    # =========================================================
    # CLOSE
    # =========================================================

    def _on_close(self) -> None:
        try:
            if self.discord is not None:
                if self.discord.connected:
                    self.discord.clear()

                self.discord.close()

        except Exception:
            pass

        self.destroy()


def main() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()