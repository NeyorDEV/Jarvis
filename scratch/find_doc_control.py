import uiautomation as auto
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# We search specifically for the Deezer window
deezer_ctrl = auto.Control(searchDepth=1, ClassName="Chrome_WidgetWin_1", Name="Deezer")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

print(f"Found window: {deezer_ctrl.Name}")

# Search for any DocumentControl
doc = deezer_ctrl.DocumentControl(searchDepth=10)
if doc.Exists(2.0):
    print(f"🎉 DocumentControl found! Name: '{doc.Name}'")
else:
    print("❌ DocumentControl not found at searchDepth=10.")

# Search for any ButtonControl
btn = deezer_ctrl.ButtonControl(searchDepth=10)
if btn.Exists(2.0):
    print(f"🎉 ButtonControl found! Name: '{btn.Name}'")
else:
    print("❌ ButtonControl not found at searchDepth=10.")

# Let's list all controls of any type under deezer_ctrl that have a non-empty name
print("\nScanning all elements under Deezer (depth=10)...")
count = 0
def scan(ctrl, depth=0):
    global count
    if count > 100:
        return
    name = ctrl.Name or ""
    ctype = ctrl.ControlTypeName or ""
    if name or ctype in ["ButtonControl", "DocumentControl"]:
        print(f"{'  ' * depth}[{ctype}] Name: '{name}' | AutoId: '{ctrl.AutomationId}'")
        count += 1
    for child in ctrl.GetChildren():
        scan(child, depth + 1)

scan(deezer_ctrl)
