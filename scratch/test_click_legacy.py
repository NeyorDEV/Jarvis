import uiautomation as auto
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

# Bring to focus
print("Bringing Deezer to focus...")
try:
    import win32gui, win32con
    candidats = []
    def _cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            titre = win32gui.GetWindowText(hwnd)
            if "Deezer" in titre:
                candidats.append(hwnd)
    win32gui.EnumWindows(_cb, None)
    if candidats:
        hwnd = candidats[0]
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
except Exception as e:
    print(f"Error focusing: {e}")

# Find AJOUTÉ header
header_added = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
if not header_added.Exists(1.0):
    print("AJOUTÉ HeaderControl not found.")
    sys.exit(1)

# Find child button
btn = header_added.ButtonControl(Name="AJOUTÉ")
if not btn.Exists(1.0):
    print("AJOUTÉ ButtonControl not found.")
    sys.exit(1)

# Try click
print(f"Clicking AJOUTÉ ButtonControl at {btn.BoundingRectangle}")
# Let's try physical click first, by moving cursor to center of rect and clicking
try:
    rect = btn.BoundingRectangle
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    print(f"Clicking at ({cx}, {cy})")
    auto.Click(cx, cy)
except Exception as e:
    print(f"Error physical click: {e}")

print("Waiting 3 seconds...")
time.sleep(3)

# Read first 5 tracks
tracks = []
def find_tracks(ctrl):
    if ctrl.ControlTypeName == "CustomControl" and ctrl.Name and "Écouter" in ctrl.Name:
        tracks.append(ctrl.Name)
    for child in ctrl.GetChildren():
        find_tracks(child)
        if len(tracks) >= 5:
            return

find_tracks(deezer_ctrl)
print("\n--- First 5 tracks after physical click ---")
for i, t in enumerate(tracks):
    print(f"Track {i}: Name='{t}'")
