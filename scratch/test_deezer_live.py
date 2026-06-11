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
    
    print(f"🚀 Launching {deezer_exe} with --force-renderer-accessibility...")
    p = subprocess.Popen(
        [deezer_exe, "--force-renderer-accessibility"],
        cwd=deezer_dir,
        shell=False
    )
    
    print("⏳ Waiting for Deezer window to appear (up to 20s)...")
    deezer_ctrl = None
    for i in range(40):
        time.sleep(0.5)
        # Chercher la fenêtre
        root = auto.GetRootControl()
        for child in root.GetChildren():
            title = child.Name or ""
            cname = child.ClassName or ""
            if "deezer" in title.lower() or "deezer" in cname.lower():
                deezer_ctrl = child
                break
        if deezer_ctrl:
            break
            
    if not deezer_ctrl:
        print("❌ Deezer window not found after 20s.")
        p.kill()
        return
        
    print(f"✔ Window found! Title: '{deezer_ctrl.Name}' | Type: {deezer_ctrl.ControlTypeName} | Class: {deezer_ctrl.ClassName} | HWND: {deezer_ctrl.NativeWindowHandle}")
    
    # Attendre encore 3 secondes pour que le document se charge
    print("⏳ Waiting 3 seconds for UI to render...")
    time.sleep(3)
    
    print("📂 Scanning for DocumentControl elements...")
    docs = deezer_ctrl.GetChildren()
    print(f"Total direct children: {len(docs)}")
    for child in docs:
        print(f" - [{child.ControlTypeName}] Name: '{child.Name}'")
        if child.ControlTypeName == "DocumentControl":
            print(f"📂 FOUND DOCUMENT CONTROL: '{child.Name}'")
            print("----------------------------------------")
            dump_interactive_elements(child)
            
    # Laisser tourner pendant 15 secondes pour vérifier si l'application reste stable
    print("⏳ Keeping process alive for 15s to check stability...")
    for remaining in range(15, 0, -5):
        print(f"   -> {remaining}s remaining...")
        time.sleep(5)
        
    # Vérifier si le process est toujours en vie
    p.poll()
    if p.returncode is not None:
        print(f"❌ Process exited unexpectedly with return code: {p.returncode}")
    else:
        print("✔ Process is still running stably! Killing it now to clean up.")
        p.kill()

if __name__ == "__main__":
    main()
