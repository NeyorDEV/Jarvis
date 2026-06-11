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

print("Scanning for headers...")

headers = []
all_controls = []

def find_headers_and_relevant(control, depth=0):
    name = control.Name or ""
    type_name = control.ControlTypeName or ""
    
    # We collect HeaderControl elements
    if "header" in type_name.lower():
        headers.append(control)
    
    # Or names like AJOUTÉ
    if "ajout" in name.lower() or "date" in name.lower():
        all_controls.append((control, depth))
        
    for child in control.GetChildren():
        find_headers_and_relevant(child, depth + 1)

find_headers_and_relevant(deezer_ctrl)

print(f"\n--- Found {len(headers)} HeaderControls ---")
for h in headers:
    print(f"Header: Name='{h.Name}', Class={h.ClassName}, Rect={h.BoundingRectangle}, SupportInvoke={hasattr(h, 'GetInvokePattern')}")
    # Print its parent and children to see context
    parent = h.GetParentControl()
    if parent:
        print(f"  Parent: Name='{parent.Name}', Type={parent.ControlTypeName}")
        for sibling in parent.GetChildren():
            print(f"    Sibling: Name='{sibling.Name}', Type={sibling.ControlTypeName}")

print(f"\n--- Found {len(all_controls)} controls containing 'ajout' or 'date' ---")
for ctrl, depth in all_controls[:20]:
    print(f"Depth {depth}: Name='{ctrl.Name}', Type={ctrl.ControlTypeName}, Rect={ctrl.BoundingRectangle}")
