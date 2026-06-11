import subprocess
import time
import ctypes
import sys
try:
    import pyautogui
except ImportError:
    pyautogui = None

sys.stdout.reconfigure(encoding='utf-8')

def get_windows_titles_with_hwnd():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    
    windows = []
    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            windows.append((hwnd, buff.value))
        return True
        
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return windows

def focus_window_by_title(title_query):
    import win32gui, win32con
    for hwnd, title in get_windows_titles_with_hwnd():
        if title_query.lower() in title.lower():
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"Erreur de focus pour {title}: {e}")
    return False

def test_focus_play():
    track_id = 66609426
    uri = f"deezer://www.deezer.com/track/{track_id}"
    
    print(f"🚀 Lancement de l'URI : {uri}")
    subprocess.Popen(["explorer", uri], shell=False)
    
    print("⏳ Attente de 5 secondes pour le chargement de la page...")
    time.sleep(5)
    
    print("🎯 Focus de la fenêtre Deezer...")
    focused = focus_window_by_title("Deezer")
    if not focused:
        print("❌ Impossible de trouver et focus la fenêtre Deezer.")
        return
        
    if pyautogui:
        print("⌨ Simulation de l'appui sur ESPACE pour lancer la lecture...")
        pyautogui.press('space')
        
        print("⏳ Attente de 4 secondes...")
        time.sleep(4)
        
        print("\n--- ÉTAT DES FENÊTRES APRÈS ESPACE ---")
        after = [t for hwnd, t in get_windows_titles_with_hwnd() if "deezer" in t.lower()]
        print(after)
        
        success = any("get lucky" in t.lower() or "daft punk" in t.lower() for t in after)
        if success:
            print("\n🎉 SUCCÈS : Le titre de la fenêtre s'est mis à jour avec le morceau !")
        else:
            # Essayer d'appuyer sur Entrée en fallback
            print("⌨ Fallback : Simulation de l'appui sur ENTRÉE...")
            pyautogui.press('enter')
            time.sleep(4)
            after2 = [t for hwnd, t in get_windows_titles_with_hwnd() if "deezer" in t.lower()]
            print("Après ENTRÉE :", after2)
            if any("get lucky" in t.lower() or "daft punk" in t.lower() for t in after2):
                print("\n🎉 SUCCÈS : Le titre s'est mis à jour après ENTRÉE !")
            else:
                print("\n❌ ÉCHEC : Aucun changement de titre.")
    else:
        print("❌ pyautogui n'est pas disponible pour simuler les touches.")

if __name__ == "__main__":
    test_focus_play()
