import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def dump_interactive_elements(control, depth=0):
    name = control.Name or ""
    c_type = control.ControlTypeName
    auto_id = control.AutomationId or ""
    
    # Si l'élément a un nom ou s'il s'agit d'un bouton/edit/texte, on l'affiche
    if name or c_type in ["ButtonControl", "EditControl", "TextControl", "HyperlinkControl"]:
        indent = "  " * depth
        print(f"{indent}- [{c_type}] Name: '{name}' | ID: '{auto_id}'")
        
    for child in control.GetChildren():
        dump_interactive_elements(child, depth + 1)

def main():
    print("🔍 Searching for Deezer Window...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(1.0):
        print("❌ Deezer not found.")
        return
        
    print("✔ Deezer window found. Scanning for DocumentControl elements...")
    docs = deezer_ctrl.GetChildren()
    for child in docs:
        if child.ControlTypeName == "DocumentControl":
            print(f"\n📂 FOUND DOCUMENT CONTROL: '{child.Name}'")
            print("----------------------------------------")
            dump_interactive_elements(child)

if __name__ == "__main__":
    main()
