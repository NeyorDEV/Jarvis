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

found_btn = None
for btn in buttons:
    curr = btn
    for _ in range(3):
        curr = curr.GetParentControl()
        if not curr:
            break
        descendants = []
        def get_descendant_names(ctrl):
            if ctrl.ControlTypeName == "ButtonControl":
                descendants.append(ctrl.Name or "")
            for child in ctrl.GetChildren():
                get_descendant_names(child)
        get_descendant_names(curr)
        if "Précédent" in descendants or "Suivant" in descendants:
            found_btn = btn
            break
    if found_btn:
        break

if found_btn:
    print(f"SUCCESS: Found player button: '{found_btn.Name}' at {found_btn.BoundingRectangle}")
else:
    print("FAILURE: Player button not found.")
