import urllib.request
import json
import subprocess
import time
import ctypes
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_windows_titles():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    
    titles = []
    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
        
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return titles

def test_deezer():
    print("🔎 Recherche d'un morceau de test sur Deezer...")
    try:
        url = "https://api.deezer.com/search?q=daft+punk+get+lucky"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            tracks = data.get("data", [])
            if not tracks:
                print("❌ Aucun morceau trouvé.")
                return
            
            track = tracks[0]
            track_id = track.get("id")
            title = track.get("title")
            artist = track.get("artist", {}).get("name", "")
            print(f"✔ Morceau trouvé : '{title}' de '{artist}' (ID: {track_id})")
            
            # 1. Vérifier l'état avant lancement
            print("\n--- ÉTAT DES FENÊTRES AVANT LANCEMENT ---")
            before = [t for t in get_windows_titles() if "deezer" in t.lower()]
            print("Fenêtres Deezer détectées :", before)
            
            # 2. Lancement du morceau
            deezer_uri = f"deezer://www.deezer.com/track/{track_id}?autoplay=true"
            print(f"\n🚀 Lancement de la commande : explorer {deezer_uri}")
            subprocess.Popen(["explorer", deezer_uri], shell=False)
            
            # 3. Attente
            print("⏳ Attente de 10 secondes pour le chargement et la lecture...")
            time.sleep(10)
            
            # 4. Vérifier l'état après lancement
            print("\n--- ÉTAT DES FENÊTRES APRÈS LANCEMENT ---")
            after = [t for t in get_windows_titles() if "deezer" in t.lower()]
            print("Fenêtres Deezer détectées :", after)
            
            # Si le titre de la fenêtre contient le nom de l'artiste/chanson, c'est que la lecture a démarré !
            success = False
            for t in after:
                if title.lower() in t.lower() or artist.lower() in t.lower():
                    success = True
                    print(f"\n🎉 SUCCÈS : La fenêtre '{t}' indique que la lecture a commencé !")
                    break
            
            if not success:
                print("\n❌ ÉCHEC : Le titre de la fenêtre n'indique pas de lecture active. L'autoplay n'a pas fonctionné ou l'application ne s'est pas lancée.")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

if __name__ == "__main__":
    test_deezer()
