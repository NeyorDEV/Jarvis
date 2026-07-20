import sys
import pychromecast
from pychromecast.controllers.youtube import YouTubeController

def execute_command(ip, cmd, value=None):
    try:
        # Recherche de la télé par IP
        chromecasts, browser = pychromecast.get_chromecasts(timeout=10)
        cast = next((cc for cc in chromecasts if cc.cast_info.host == ip), None)
        browser.stop_discovery()

        if not cast:
            print("ERROR: TV not found")
            return

        cast.wait()

        if cmd == "off":
            cast.quit_app()
            print("SUCCESS: TV stopped")
        elif cmd == "pause":
            cast.media_controller.pause()
            print("SUCCESS: TV paused")
        elif cmd == "play":
            cast.media_controller.play()
            print("SUCCESS: TV playing")
        elif cmd == "youtube":
            yt = YouTubeController()
            cast.register_handler(yt)
            yt.play_video(value)
            print(f"SUCCESS: YouTube {value} started")
        elif cmd == "volume":
            current_vol = cast.status.volume_level
            new_vol = min(current_vol + 0.1, 1.0) if value == "up" else max(current_vol - 0.1, 0.0)
            cast.set_volume(new_vol)
            print(f"SUCCESS: Volume {value}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        ip_addr = sys.argv[1]
        command = sys.argv[2]
        val = sys.argv[3] if len(sys.argv) > 3 else None
        execute_command(ip_addr, command, val)
