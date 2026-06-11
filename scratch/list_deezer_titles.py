import win32gui

def enum_cb(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if title or class_name:
            results.append((hwnd, title, class_name))

results = []
win32gui.EnumWindows(enum_cb, results)
print("Visible Windows:")
for hwnd, title, class_name in results:
    if "deezer" in title.lower() or "deezer" in class_name.lower():
        print(f"HWND: {hwnd}, Title: '{title}', Class: '{class_name}'")
