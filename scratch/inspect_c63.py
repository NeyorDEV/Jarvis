import uiautomation as auto
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

print("Deezer window found.")

# Try to find DocumentControl
doc_ctrl = deezer_ctrl.DocumentControl(searchDepth=3)
if doc_ctrl.Exists(0.5):
    print(f"DocumentControl Name: '{doc_ctrl.Name}'")
else:
    print("DocumentControl not found.")

# Print all child controls of deezer_ctrl down to depth 3 to see the structure
def print_tree(control, depth=0):
    indent = "  " * depth
    name = control.Name or ""
    ctype = control.ControlTypeName or ""
    print(f"{indent}{ctype}: '{name}' (Rect: {control.BoundingRectangle})")
    if depth < 3:
        for child in control.GetChildren():
            print_tree(child, depth + 1)

print("\nPrinting control tree (depth 3):")
print_tree(deezer_ctrl)
