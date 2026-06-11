import subprocess
import os
import time
import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

def ensure_deezer_accessible():
    r = subprocess.run("tasklist /FI \"IMAGENAME eq Deezer.exe\"", shell=True, capture_output=True, text=True)
    if "Deezer.exe" not in r.stdout:
        print("🚀 Launching Deezer with accessibility...")
        subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility"], cwd=DEEZER_DIR, shell=False)
        time.sleep(8)
    else:
        print("✔ Deezer is already running.")

def get_track_info():
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    if not deezer_ctrl.Exists(1.0):
        return None
    for child in deezer_ctrl.GetChildren():
        if child.ControlTypeName == "DocumentControl":
            title = child.Name
            if title and " - Deezer" in title:
                return title.replace(" - Deezer", "").strip()
    return None

def click_player_button(button_names):
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    if not deezer_ctrl.Exists(1.0):
        return False
        
    buttons = []
    def _collect_buttons(control):
        if control.ControlTypeName == "ButtonControl":
            name = control.Name or ""
            if name in button_names or any(b in name for b in button_names):
                buttons.append(control)
        for child in control.GetChildren():
            _collect_buttons(child)
            
    _collect_buttons(deezer_ctrl)
    
    # Filter for the main player control bar
    target_btn = None
    for btn in buttons:
        parent = btn.GetParentControl()
        if parent:
            siblings = [c.Name for c in parent.GetChildren() if c.ControlTypeName == "ButtonControl"]
            if "Suivant" in siblings or "Précédent" in siblings:
                target_btn = btn
                break
                
    if not target_btn and buttons:
        target_btn = buttons[0]
        
    if target_btn:
        print(f"🖱 Clicking button '{target_btn.Name}'...")
        target_btn.Click()
        return True
    return False

def main():
    # 1. Start accessible Deezer
    ensure_deezer_accessible()
    
    # 2. Check current track before loading new one
    curr = get_track_info()
    print(f"🎵 Current track: {curr}")
    
    # 3. Load Daft Punk - Get Lucky (track ID: 66609426)
    track_id = 66609426
    uri = f"deezer://www.deezer.com/track/{track_id}"
    print(f"🚀 Loading track URI: {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    # Wait for the track page to load
    print("⏳ Waiting 5 seconds for page load...")
    time.sleep(5)
    
    # 4. Check loaded track metadata
    new_track = get_track_info()
    print(f"🎵 Loaded track: {new_track}")
    
    # 5. Click Play (named 'Écouter' or 'Pause' / 'Mettre en pause')
    # If the song is already playing or paused, we click it to toggle
    click_player_button(["Écouter", "Pause", "Mettre en pause"])
    
    time.sleep(2)
    print(f"🎵 Track state after play command: {get_track_info()}")

if __name__ == "__main__":
    main()
