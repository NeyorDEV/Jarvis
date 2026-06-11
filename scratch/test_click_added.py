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

print("Clicking 'AJOUTÉ' button...")
pattern = btn.GetInvokePattern()
if pattern:
    pattern.Invoke()
else:
    btn.Click(simulateMove=False)

print("Waiting 2 seconds for sort to apply...")
time.sleep(2)

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
print("\n--- First 5 tracks after click ---")
for i, t in enumerate(tracks):
    print(f"Track {i}: Name='{t}'")
