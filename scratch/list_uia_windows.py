import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def main():
    print("🔍 Listing all top-level windows with uiautomation...")
    root = auto.GetRootControl()
    children = root.GetChildren()
    print(f"Total top-level windows: {len(children)}")
    for child in children:
        name = child.Name or "<No Name>"
        class_name = child.ClassName or "<No Class>"
        control_type = child.ControlTypeName
        if "deezer" in name.lower() or "deezer" in class_name.lower():
            print(f"⭐ FOUND DEEZER:")
        print(f" - [{control_type}] Title: '{name}' | Class: '{class_name}' | HWND: {child.NativeWindowHandle}")

if __name__ == "__main__":
    main()
