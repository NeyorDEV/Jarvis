"""
Exploration de la structure UIA de la barre de recherche Deezer et ses résultats.
"""
import sys, os, time, subprocess, psutil, pyautogui
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from controller.deezer_controller import get_deezer_main_control, _focus_deezer

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
DEST = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"

# Lancer Deezer
print("Killing + launching Deezer...")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try: proc.kill()
        except: pass
time.sleep(2)
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility"], cwd=DEEZER_DIR, shell=False)
print("Waiting 8s...")
time.sleep(8)
_focus_deezer()
time.sleep(1)

ctrl = get_deezer_main_control()
if not ctrl:
    print("Main control not found"); sys.exit(1)

# --- Chercher la barre de recherche ---
print("\n=== Searching for search bar (EditControl / role=searchbox) ===")
search_candidates = []
def find_search_controls(c, depth=0):
    ctype = c.ControlTypeName or ""
    name = c.Name or ""
    if ctype == "EditControl":
        rect = c.BoundingRectangle
        print(f"{'  '*depth}EditControl | Name='{name}' | Rect={rect.left},{rect.top},{rect.right},{rect.bottom}")
        search_candidates.append(c)
    if depth < 8:
        for child in c.GetChildren():
            find_search_controls(child, depth+1)

find_search_controls(ctrl)

if not search_candidates:
    print("No EditControl found!")
    sys.exit(1)

# Prendre le premier EditControl (la barre de recherche)
search_box = search_candidates[0]
print(f"\nUsing search box: '{search_box.Name}' | Rect={search_box.BoundingRectangle}")

# --- Cliquer et taper ---
print("\nClicking search bar and typing 'c63 werenoi'...")
try:
    search_box.Click(simulateMove=False)
    time.sleep(0.5)
except Exception as e:
    print(f"Click failed: {e}, trying physical click...")
    rect = search_box.BoundingRectangle
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    pyautogui.click(cx, cy)
    time.sleep(0.5)

# Effacer et taper
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.2)
pyautogui.write('c63 werenoi', interval=0.08)
print("Typed. Waiting 2s for results...")
time.sleep(2)

# Screenshot de l'état actuel
shot = pyautogui.screenshot()
shot.save(os.path.join(DEST, "search_results_screenshot.png"))
print("Screenshot saved.")

# --- Dumper l'arbre UIA des résultats ---
print("\n=== UIA tree after typing (looking for results) ===")
ctrl_after = get_deezer_main_control()
if ctrl_after:
    def dump_tree_filtered(c, depth=0, max_depth=8):
        ctype = c.ControlTypeName or ""
        name = c.Name or ""
        rect = c.BoundingRectangle
        # Afficher seulement les éléments intéressants
        if ctype in ["ButtonControl", "EditControl", "ListItemControl", "CustomControl", "DataItemControl"] and name:
            print(f"{'  '*depth}[{ctype}] '{name[:80]}' | {rect.left},{rect.top},{rect.right},{rect.bottom}")
        if depth < max_depth:
            for child in c.GetChildren():
                dump_tree_filtered(child, depth+1, max_depth)
    dump_tree_filtered(ctrl_after)
