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
    
    print(f"🚀 Launching {deezer_exe} with --force-renderer-accessibility...")
    # Lancement direct avec cwd
    p = subprocess.Popen([deezer_exe, "--force-renderer-accessibility"], cwd=deezer_dir, shell=False)
    
    print("⏳ Waiting 8 seconds for the window to load...")
    time.sleep(8)
    
    print("🔍 Looking for Deezer window...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(1.0):
        # Lister les fenêtres pour voir s'il y a un autre nom ou si le process est mort
        print("❌ Window 'Deezer' not found. Checking if process is still running...")
        p.poll()
        if p.returncode is not None:
            print(f"❌ Process exited with return code: {p.returncode}")
        else:
            print("✔ Process is still running! Listing top level windows:")
            root = auto.GetRootControl()
            for child in root.GetChildren():
                name = child.Name or "<No Name>"
                cname = child.ClassName or "<No Class>"
                if "deezer" in name.lower() or "deezer" in cname.lower():
                    print(f" - [{child.ControlTypeName}] Name: '{name}' | Class: '{cname}'")
        return
        
    print(f"✔ Window found! Title: '{deezer_ctrl.Name}' | Type: {deezer_ctrl.ControlTypeName}")
    print("🌳 Walking children up to depth 3...")
    for child in deezer_ctrl.GetChildren():
        name = child.Name or "<No Name>"
        c_type = child.ControlTypeName
        print(f" - [{c_type}] '{name}'")
        for sub in child.GetChildren():
            print(f"   + [{sub.ControlTypeName}] '{sub.Name or '<No Name>'}'")
            for sub_sub in sub.GetChildren():
                print(f"     * [{sub_sub.ControlTypeName}] '{sub_sub.Name or '<No Name>'}'")

if __name__ == "__main__":
    main()
