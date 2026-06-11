import uiautomation as auto
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

button_names = ["Écouter", "Pause", "Mettre en pause"]
buttons = []

def _collect_buttons(control):
    if control.ControlTypeName == "ButtonControl":
        name = control.Name or ""
        if name in button_names or any(b in name for b in button_names):
            try:
                rect = control.BoundingRectangle
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                if width > 0 and height > 0:
                    buttons.append(control)
            except:
                pass
    for child in control.GetChildren():
        _collect_buttons(child)

_collect_buttons(deezer_ctrl)
print(f"Collected {len(buttons)} candidates.")

for idx, btn in enumerate(buttons):
    print(f"\nCandidate {idx}: '{btn.Name}' at {btn.BoundingRectangle}")
    parent = btn.GetParentControl()
    if parent:
        print(f"  Parent: Type={parent.ControlTypeName}, Name='{parent.Name}'")
        grandparent = parent.GetParentControl()
        if grandparent:
            print(f"    Grandparent: Type={grandparent.ControlTypeName}, Name='{grandparent.Name}'")
            # Let's print the entire tree under grandparent up to depth 2
            def print_tree(ctrl, depth=0):
                indent = "      " * depth
                print(f"{indent}- Name='{ctrl.Name}', Type={ctrl.ControlTypeName}")
                if depth < 2:
                    for child in ctrl.GetChildren():
                        print_tree(child, depth + 1)
            print_tree(grandparent)
