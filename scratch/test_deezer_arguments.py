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
    print("🚀 Terminating any running Deezer instances...")
    subprocess.run("taskkill /IM Deezer.exe /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    deezer_dir = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
    deezer_exe = os.path.join(deezer_dir, "Deezer.exe")
    track_uri = "deezer://www.deezer.com/track/66609426" # Get Lucky
    
    print(f"🚀 Launching {deezer_exe} with accessibility and track URI...")
    # Lancer avec les deux arguments
    subprocess.Popen([deezer_exe, "--force-renderer-accessibility", track_uri], cwd=deezer_dir, shell=False)
    
    print("⏳ Waiting 10 seconds for window and track to load...")
    time.sleep(10)
    
    print("🔍 Searching for Deezer window...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(1.0):
        print("❌ Deezer window not found.")
        return
        
    print(f"✔ Window found! HWND: {deezer_ctrl.NativeWindowHandle}")
    
    # Trouver le DocumentControl
    song_info = None
    for child in deezer_ctrl.GetChildren():
        if child.ControlTypeName == "DocumentControl":
            title = child.Name
            if title and " - Deezer" in title:
                song_info = title.replace(" - Deezer", "").strip()
                break
                
    print(f"🎵 Currently loaded track: {song_info}")
    
    # Cliquer sur Play/Écouter
    print("🖱 Attempting to click Play button...")
    buttons = []
    def _collect_buttons(control):
        if control.ControlTypeName == "ButtonControl":
            name = control.Name or ""
            if name in ["Écouter", "Pause", "Mettre en pause"] or any(b in name for b in ["Écouter", "Pause"]):
                buttons.append(control)
        for child in control.GetChildren():
            _collect_buttons(child)
            
    _collect_buttons(deezer_ctrl)
    
    target_btn = None
    for btn in buttons:
        parent = btn.GetParentControl()
        if parent:
            siblings = [c.Name for c in parent.GetChildren() if c.ControlTypeName == "ButtonControl"]
            if "Suivant" in siblings or "Précédent" in siblings:
                target_btn = btn
                break
                
    if target_btn:
        print(f"✔ Clicked: '{target_btn.Name}'")
        target_btn.Click()
    else:
        print("❌ Play button not found in UIA tree.")

if __name__ == "__main__":
    main()
