import uiautomation as auto
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("Searching for Deezer window...")
deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

# Find header
header_added = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
if not header_added.Exists(1.0):
    print("AJOUTÉ HeaderControl not found.")
    sys.exit(1)

print("--- AJOUTÉ HeaderControl details ---")
print(f"Name: {header_added.Name}")
print(f"ControlTypeName: {header_added.ControlTypeName}")
print(f"BoundingRectangle: {header_added.BoundingRectangle}")
print(f"HasKeyboardFocus: {header_added.HasKeyboardFocus}")

# Check its children
children = header_added.GetChildren()
print(f"Number of children: {len(children)}")
for i, child in enumerate(children):
    print(f"Child {i}: Name='{child.Name}', Type={child.ControlTypeName}, Rect={child.BoundingRectangle}")
    # Print pattern support
    print(f"  LegacyIAccessiblePattern support: {hasattr(child, 'GetLegacyIAccessiblePattern')}")
    try:
        legacy = child.GetLegacyIAccessiblePattern()
        if legacy:
            print(f"    Value: {legacy.Value}")
            print(f"    Description: {legacy.Description}")
            print(f"    State: {legacy.State}")
            print(f"    DefaultAction: {legacy.DefaultAction}")
    except Exception as e:
        print(f"    Legacy error: {e}")

# Check parent
parent = header_added.GetParentControl()
if parent:
    print(f"\nParent of Header: Type={parent.ControlTypeName}")
    # Let's inspect the first few items in the list to get their 'added date'
    # The tracks seem to be CustomControl elements under some group
    # Let's list the first 3 CustomControls that represent tracks
    tracks = []
    def find_tracks(ctrl):
        if ctrl.ControlTypeName == "CustomControl" and ctrl.Name and "Écouter" in ctrl.Name:
            tracks.append(ctrl)
        for child in ctrl.GetChildren():
            find_tracks(child)
            if len(tracks) >= 3:
                return
    find_tracks(deezer_ctrl)
    print("\n--- First 3 tracks ---")
    for i, t in enumerate(tracks):
        print(f"Track {i}: Name='{t.Name}'")
