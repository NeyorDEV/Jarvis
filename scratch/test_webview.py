import os
import sys
import webview

def test():
    print("Testing pywebview initialization with edgehtml...")
    _app_data = os.getenv("LOCALAPPDATA", os.getenv("APPDATA", os.path.expanduser("~")))
    _storage_path = os.path.join(_app_data, "JARVIS_Test")
    print(f"Using storage path: {_storage_path}")
    
    # Create window
    win = webview.create_window("Test JARVIS", "https://google.com")
    
    try:
        # Start webview using edgehtml GUI engine
        webview.start(gui="edgehtml", private_mode=False, storage_path=_storage_path, debug=True)
        print("Success!")
    except Exception as e:
        print(f"Error during webview.start: {e}")

if __name__ == "__main__":
    test()
