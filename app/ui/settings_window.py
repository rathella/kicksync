from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Optional

import customtkinter as ctk


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

ACCENT = "#53FC18"
ACCENT_HOVER = "#68FF35"

BG = "#18181B"
CARD = "#232326"
CARD_ALT = "#202024"
BORDER = "#343438"

TEXT = "#F4F4F5"
TEXT_SECONDARY = "#A1A1AA"
MUTED = "#71717A"
ERROR = "#FF5C68"


class SettingsWindow(ctk.CTkToplevel):
    def __init__(
        self,
        parent: Any,
        on_saved: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)

        self.parent_window = parent
        self.on_saved = on_saved

        self.title("KickSync Settings")
        self.geometry("440x560")
        self.resizable(False, False)

        self.transient(parent)

        self._build_ui()
        self._load_config()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self) -> None:
        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.main = ctk.CTkFrame(
            self,
            fg_color=BG,
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
            padx=25,
            pady=(23, 0),
        )

        title = ctk.CTkLabel(
            header,
            text="Settings",
            text_color=TEXT,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=23,
                weight="bold",
            ),
            anchor="w",
        )

        title.pack(
            anchor="w",
        )

        subtitle = ctk.CTkLabel(
            header,
            text="KickSync bağlantı ve uygulama ayarları",
            text_color=MUTED,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
            anchor="w",
        )

        subtitle.pack(
            anchor="w",
            pady=(1, 0),
        )

        # -----------------------------------------------------
        # FORM
        # -----------------------------------------------------

        form = ctk.CTkFrame(
            self.main,
            fg_color="transparent",
        )

        form.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=(22, 0),
        )

        form.grid_columnconfigure(
            0,
            weight=1,
        )

        self.kick_url = self._create_entry(
            form,
            row=0,
            label="Kick URL",
            placeholder="https://kick.com/kullanici",
        )

        self.discord_client_id = self._create_entry(
            form,
            row=2,
            label="Discord Application ID",
            placeholder="Discord Application ID",
        )

        self.poll_interval = self._create_entry(
            form,
            row=4,
            label="Yenileme aralığı",
            placeholder="5",
        )

        self.poll_interval.insert(
            0,
            "5",
        )

        # -----------------------------------------------------
        # OPTIONS
        # -----------------------------------------------------

        options = ctk.CTkFrame(
            form,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
            corner_radius=10,
        )

        options.grid(
            row=6,
            column=0,
            sticky="ew",
            pady=(20, 0),
        )

        options.grid_columnconfigure(
            0,
            weight=1,
        )

        self.start_with_windows = ctk.CTkSwitch(
            options,
            text="Windows açılışında başlat",
            text_color=TEXT_SECONDARY,
            progress_color=ACCENT,
            button_color="#D4D4D8",
            button_hover_color="#E4E4E7",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
        )

        self.start_with_windows.grid(
            row=0,
            column=0,
            sticky="w",
            padx=14,
            pady=(13, 7),
        )

        self.minimize_to_tray = ctk.CTkSwitch(
            options,
            text="Kapatınca sistem tepsisine küçült",
            text_color=TEXT_SECONDARY,
            progress_color=ACCENT,
            button_color="#D4D4D8",
            button_hover_color="#E4E4E7",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
            ),
        )

        self.minimize_to_tray.grid(
            row=1,
            column=0,
            sticky="w",
            padx=14,
            pady=(7, 13),
        )

        # -----------------------------------------------------
        # LANGUAGE / THEME
        # -----------------------------------------------------

        self.language = self._create_option(
            form,
            row=7,
            label="Dil",
            values=[
                "Türkçe",
                "English",
            ],
        )

        self.theme = self._create_option(
            form,
            row=9,
            label="Tema",
            values=[
                "Dark",
                "Light",
                "System",
            ],
        )

        # -----------------------------------------------------
        # BUTTONS
        # -----------------------------------------------------

        buttons = ctk.CTkFrame(
            self.main,
            fg_color="transparent",
        )

        buttons.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(22, 23),
        )

        buttons.grid_columnconfigure(
            0,
            weight=1,
        )

        buttons.grid_columnconfigure(
            1,
            weight=1,
        )

        cancel_button = ctk.CTkButton(
            buttons,
            text="İptal",
            height=39,
            corner_radius=8,
            fg_color=CARD_ALT,
            hover_color="#29292E",
            border_width=1,
            border_color="#36363B",
            text_color="#C4C4CA",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
            command=self.destroy,
        )

        cancel_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )

        save_button = ctk.CTkButton(
            buttons,
            text="Kaydet",
            height=39,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#101510",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold",
            ),
            command=self._save_config,
        )

        save_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(4, 0),
        )

    def _create_entry(
        self,
        parent: Any,
        row: int,
        label: str,
        placeholder: str,
    ) -> ctk.CTkEntry:
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            anchor="w",
        )

        label_widget.grid(
            row=row,
            column=0,
            sticky="w",
            pady=(0, 6),
        )

        entry = ctk.CTkEntry(
            parent,
            height=37,
            corner_radius=8,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text=placeholder,
            placeholder_text_color="#5F5F67",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
        )

        entry.grid(
            row=row + 1,
            column=0,
            sticky="ew",
        )

        return entry

    def _create_option(
        self,
        parent: Any,
        row: int,
        label: str,
        values: list[str],
    ) -> ctk.CTkComboBox:
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=10,
                weight="bold",
            ),
            anchor="w",
        )

        label_widget.grid(
            row=row,
            column=0,
            sticky="w",
            pady=(18, 6),
        )

        combo = ctk.CTkComboBox(
            parent,
            height=37,
            corner_radius=8,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
            button_color=CARD,
            button_hover_color="#29292E",
            dropdown_fg_color=CARD,
            dropdown_hover_color="#2D2D31",
            dropdown_text_color=TEXT,
            text_color=TEXT,
            values=values,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
        )

        combo.grid(
            row=row + 1,
            column=0,
            sticky="ew",
        )

        return combo

    # =========================================================
    # CONFIG
    # =========================================================

    def _load_config(self) -> None:
        if not CONFIG_PATH.exists():
            return

        try:
            with CONFIG_PATH.open(
                "r",
                encoding="utf-8",
            ) as file:
                config: dict[str, Any] = json.load(
                    file,
                )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return

        self.kick_url.delete(
            0,
            "end",
        )

        self.kick_url.insert(
            0,
            str(
                config.get(
                    "kick_url",
                    "",
                )
            ),
        )

        self.discord_client_id.delete(
            0,
            "end",
        )

        self.discord_client_id.insert(
            0,
            str(
                config.get(
                    "discord_client_id",
                    "",
                )
            ),
        )

        self.poll_interval.delete(
            0,
            "end",
        )

        self.poll_interval.insert(
            0,
            str(
                config.get(
                    "poll_interval",
                    5,
                )
            ),
        )

        if config.get(
            "start_with_windows",
            False,
        ):
            self.start_with_windows.select()

        if config.get(
            "minimize_to_tray",
            False,
        ):
            self.minimize_to_tray.select()

        language = str(
            config.get(
                "language",
                "Türkçe",
            )
        )

        if language not in (
            "Türkçe",
            "English",
        ):
            language = "Türkçe"

        self.language.set(
            language,
        )

        theme = str(
            config.get(
                "theme",
                "Dark",
            )
        )

        if theme not in (
            "Dark",
            "Light",
            "System",
        ):
            theme = "Dark"

        self.theme.set(
            theme,
        )

    # =========================================================
    # SAVE
    # =========================================================

    def _save_config(self) -> None:
        kick_url = self.kick_url.get().strip()

        discord_client_id = (
            self.discord_client_id.get().strip()
        )

        if not kick_url:
            self._show_error(
                "Kick URL boş bırakılamaz.",
            )
            return

        if not discord_client_id:
            self._show_error(
                "Discord Application ID boş bırakılamaz.",
            )
            return

        try:
            poll_interval = int(
                self.poll_interval.get().strip(),
            )

        except ValueError:
            self._show_error(
                "Yenileme aralığı sayı olmalı.",
            )
            return

        poll_interval = max(
            1,
            min(
                poll_interval,
                3600,
            ),
        )

        config: dict[str, Any] = {
            "discord_client_id": discord_client_id,
            "kick_url": kick_url,
            "poll_interval": poll_interval,
            "start_with_windows": (
                self.start_with_windows.get()
                == 1
            ),
            "minimize_to_tray": (
                self.minimize_to_tray.get()
                == 1
            ),
            "language": self.language.get(),
            "theme": self.theme.get(),
        }

        try:
            with CONFIG_PATH.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    config,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

        except OSError as exc:
            self._show_error(
                f"Ayarlar kaydedilemedi:\n{exc}",
            )
            return

        if self.on_saved is not None:
            self.on_saved()

        self.destroy()

    # =========================================================
    # ERROR
    # =========================================================

    def _show_error(
        self,
        message: str,
    ) -> None:
        error_window = ctk.CTkToplevel(self)

        error_window.title("KickSync")
        error_window.geometry("360x180")
        error_window.resizable(False, False)
        error_window.transient(self)
        error_window.grab_set()

        frame = ctk.CTkFrame(
            error_window,
            fg_color=BG,
            corner_radius=0,
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        label = ctk.CTkLabel(
            frame,
            text=message,
            text_color=TEXT,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
            ),
            wraplength=310,
        )

        label.pack(
            expand=True,
            pady=(20, 8),
        )

        button = ctk.CTkButton(
            frame,
            text="Tamam",
            width=100,
            height=35,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#101510",
            command=error_window.destroy,
        )

        button.pack(
            pady=(0, 20),
        )