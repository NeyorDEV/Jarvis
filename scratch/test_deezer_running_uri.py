import subprocess
import os
import time
import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def main():
    deezer_dir = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
    deezer_exe = os.path.join(deezer_dir, "Deezer.exe")
    track_uri = "deezer://www.deezer.com/track/66609426" # Get Lucky
    
    print("🚀 App should already be running. Sending track URI directly to Deezer.exe...")
    subprocess.Popen([deezer_exe, track_uri], cwd=deezer_dir, shell=False)
    
    print("⏳ Waiting 5 seconds...")
    time.sleep(5)
    
    print("🔍 Searching for Deezer window...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    if deezer_ctrl.Exists(1.0):
        # Trouver le DocumentControl
        song_info = None
        for child in deezer_ctrl.GetChildren():
            if child.ControlTypeName == "DocumentControl":
                title = child.Name
                if title and " - Deezer" in title:
                    song_info = title.replace(" - Deezer", "").strip()
                    break
        print(f"🎵 Currently loaded track: {song_info}")
    else:
        print("❌ Deezer not found.")

if __name__ == "__main__":
    main()
