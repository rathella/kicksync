import threading
import time
import webbrowser

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from app.kick.client import KickClient
from app.discord.presence import DiscordPresenceManager
from app.state import AppState


class MainWindow:
    def __init__(self, state: AppState):
        self.state = state
        if ctk is None:
            raise ImportError("customtkinter yüklü değil.")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.root = ctk.CTk()
        self.root.title("KickSync - Kick & Discord Sync")
        self.root.geometry("450x420")
        self.root.resizable(False, False)

        self.kick_url = self.state.get("kick_url", "https://kick.com/rathellaizm")
        self.client_id = self.state.get("discord_client_id", "1547766245993226380")
        self.poll_interval = int(self.state.get("poll_interval", 5))

        self.kick_client = KickClient(self.kick_url)
        self.presence_mgr = DiscordPresenceManager(self.client_id)

        self.running = True
        self._build_ui()
        self._start_thread()

    def _build_ui(self):
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="KickSync",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_lbl.pack(side="left")

        self.badge_lbl = ctk.CTkLabel(
            self.header_frame,
            text="● OFFLINE",
            text_color="#FF5555",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.badge_lbl.pack(side="right")

        self.card = ctk.CTkFrame(self.root, corner_radius=12)
        self.card.pack(fill="x", padx=20, pady=10)

        self.stream_title_lbl = ctk.CTkLabel(
            self.card,
            text="Yayın durumu kontrol ediliyor...",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=390,
            justify="left"
        )
        self.stream_title_lbl.pack(anchor="w", padx=15, pady=(12, 4))

        self.stream_cat_lbl = ctk.CTkLabel(
            self.card,
            text="Kanal: " + self.kick_client.channel_name,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.stream_cat_lbl.pack(anchor="w", padx=15, pady=(0, 8))

        self.info_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.viewers_lbl = ctk.CTkLabel(
            self.info_frame,
            text="İzleyici: -",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.viewers_lbl.pack(side="left")

        self.discord_lbl = ctk.CTkLabel(
            self.info_frame,
            text="Discord: Bağlanıyor...",
            text_color="#888888",
            font=ctk.CTkFont(size=11)
        )
        self.discord_lbl.pack(side="right")

        self.btn_open = ctk.CTkButton(
            self.root,
            text="Yayını Aç",
            fg_color="#53FC18",
            hover_color="#45DB12",
            text_color="#000000",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=18,
            command=self._open_channel
        )
        self.btn_open.pack(fill="x", padx=20, pady=(10, 5))

        self.status_lbl = ctk.CTkLabel(
            self.root,
            text="OBS'ten yayın açtığınızda Discord otomatik güncellenecektir.",
            font=ctk.CTkFont(size=10),
            text_color="#777777"
        )
        self.status_lbl.pack(pady=10)

    def _open_channel(self):
        webbrowser.open(self.kick_client.get_channel_url())

    def _start_thread(self):
        t = threading.Thread(target=self._worker_loop, daemon=True)
        t.start()

    def _worker_loop(self):
        while self.running:
            try:
                st = self.kick_client.get_livestream_status()
                self.presence_mgr.update_presence(st)

                def update_ui():
                    if st.is_live:
                        self.badge_lbl.configure(text="● LIVE", text_color="#53FC18")
                        self.stream_title_lbl.configure(text=st.session_title or "Canlı Yayın")
                        self.stream_cat_lbl.configure(text=f"Kategori: {st.category_name}")
                        self.viewers_lbl.configure(text=f"İzleyici: {st.viewer_count:,}")
                    else:
                        self.badge_lbl.configure(text="● OFFLINE", text_color="#FF5555")
                        self.stream_title_lbl.configure(text="Yayın şu anda kapalı.")
                        self.stream_cat_lbl.configure(text=f"Kanal: {self.kick_client.channel_name}")
                        self.viewers_lbl.configure(text="İzleyici: 0")

                    if self.presence_mgr.is_connected:
                        self.discord_lbl.configure(text="Discord: Bağlı 🟢", text_color="#53FC18")
                    else:
                        self.discord_lbl.configure(text="Discord: Bağlantı Bekleniyor", text_color="#FFAA00")

                self.root.after(0, update_ui)
            except Exception:
                pass

            time.sleep(self.poll_interval)

    def run(self):
        self.root.mainloop()
        self.running = False
