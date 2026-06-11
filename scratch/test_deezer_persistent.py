import subprocess
import os
import time
import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def dump_interactive_elements(control, depth=0):
    name = control.Name or ""
    c_type = control.ControlTypeName
    auto_id = control.AutomationId or ""
    
    if name or c_type in ["ButtonControl", "EditControl", "TextControl", "HyperlinkControl"]:
        indent = "  " * depth
        print(f"{indent}- [{c_type}] Name: '{name}' | ID: '{auto_id}'")
        
    for child in control.GetChildren():
        dump_interactive_elements(child, depth + 1)

def main():
    print("🚀 Terminating any running Deezer instances...")
    subprocess.run("taskkill /IM Deezer.exe /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    deezer_dir = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
    deezer_exe = os.path.join(deezer_dir, "Deezer.exe")
    
    print(f"🚀 Launching {deezer_exe} with --force-renderer-accessibility in detached mode...")
    DETACHED_PROCESS = 0x00000008
    # Lancement détaché
    p = subprocess.Popen(
        [deezer_exe, "--force-renderer-accessibility"],
        cwd=deezer_dir,
        creationflags=DETACHED_PROCESS,
        shell=False
    )
    
    print("⏳ Waiting 10 seconds for the window to load...")
    time.sleep(10)
    
    print("🔍 Looking for Deezer window...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(1.0):
        print("❌ Deezer not found.")
        return
        
    print(f"✔ Window found! Title: '{deezer_ctrl.Name}' | Type: {deezer_ctrl.ControlTypeName}")
    print("📂 Scanning for DocumentControl elements...")
    docs = deezer_ctrl.GetChildren()
    for child in docs:
        if child.ControlTypeName == "DocumentControl":
            print(f"\n📂 FOUND DOCUMENT CONTROL: '{child.Name}'")
            print("----------------------------------------")
            dump_interactive_elements(child)

if __name__ == "__main__":
    main()
