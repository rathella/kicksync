"""
KickSync - Windows Desktop Main Entry Point
OBS'ten Kick yayını açtığınızda arka planda otomatik algılar ve Discord'a Rich Presence gönderir.
"""
import sys
import time
from app.state import AppState
from app.kick.client import KickClient
from app.discord.presence import DiscordPresenceManager


def run_background_sync(state: AppState):
    print("=" * 60)
    print("      KickSync - Discord Rich Presence Background Service")
    print("=" * 60)
    
    kick_url = state.get("kick_url", "https://kick.com/rathellaizm")
    client_id = state.get("discord_client_id", "1547766245993226380")
    poll_interval = max(3, int(state.get("poll_interval", 5)))

    print(f"[*] Takip edilen Kick kanalı: {kick_url}")
    print(f"[*] Discord Client ID: {client_id}")
    print(f"[*] Kontrol periyodu: {poll_interval} saniye")
    print("[*] Durum: Hazır. OBS'ten yayın açıldığında Discord'unuz")
    print("    otomatik olarak 'Yayında' olacaktır!")
    print("=" * 60)

    try:
        kick_client = KickClient(kick_url)
    except Exception as e:
        print(f"[!] Hata: {e}")
        return

    presence_manager = DiscordPresenceManager(client_id)
    last_live_state = None

    while True:
        try:
            status = kick_client.get_livestream_status()
            if status.is_live != last_live_state:
                last_live_state = status.is_live
                if status.is_live:
                    print(f"\n[+] CANLI YAYIN BASLADI!")
                    print(f"    Baslik: {status.session_title}")
                    print(f"    Kategori: {status.category_name}")
                    print(f"    Izleyici: {status.viewer_count:,}")
                    print(f"    -> Discord profiliniz 'Yayinda' olarak guncellendi!")
                else:
                    print(f"\n[-] YAYIN KAPANDI (Offline).")
                    print(f"    -> Discord durumu temizlendi.")

            presence_manager.update_presence(status)
        except Exception:
            pass

        time.sleep(poll_interval)


def main():
    state = AppState()
    # Eğer GUI çalıştırılabiliyorsa pencereyi aç, yoksa arka planda çalış
    try:
        from app.ui.main_window import MainWindow
        app = MainWindow(state)
        app.run()
    except Exception as e:
        run_background_sync(state)


if __name__ == "__main__":
    main()
