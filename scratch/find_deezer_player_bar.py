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
    # Let's climb up to find an ancestor that contains 'Précédent' or 'Suivant'
    curr = btn
    found_player = False
    for level in range(1, 5):
        curr = curr.GetParentControl()
        if not curr:
            break
        print(f"  Level {level}: Type={curr.ControlTypeName}, Name='{curr.Name}'")
        
        # Collect all ButtonControl descendants of this ancestor
        descendants = []
        def get_descendants(ctrl):
            if ctrl.ControlTypeName == "ButtonControl":
                descendants.append(ctrl.Name or "")
            for child in ctrl.GetChildren():
                get_descendants(child)
        get_descendants(curr)
        print(f"    Descendants: {descendants}")
        if "Précédent" in descendants or "Suivant" in descendants:
            print(f"    -> MATCHED at Level {level}!")
            found_player = True
            break
