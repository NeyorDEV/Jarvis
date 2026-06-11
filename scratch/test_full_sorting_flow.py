import time
import asyncio
import subprocess
import os
import requests
import re
from datetime import datetime

try:
    import uiautomation as auto
except ImportError:
    auto = None

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

def _sort_playlist_dechronologique(deezer_ctrl):
    try:
        header_added = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
        if not header_added.Exists(0.5):
            print("[DEEZER UIA] En-tête 'AJOUTÉ' introuvable.")
            return False
            
        btn = header_added.ButtonControl(Name="AJOUTÉ")
        if not btn.Exists(0.5):
            print("[DEEZER UIA] Bouton de tri 'AJOUTÉ' introuvable.")
            return False
            
        tracks = []
        def find_tracks(ctrl):
            if ctrl.ControlTypeName == "CustomControl" and ctrl.Name and "Écouter" in ctrl.Name:
                tracks.append(ctrl.Name)
            for child in ctrl.GetChildren():
                find_tracks(child)
                if len(tracks) >= 15:
                    return
        find_tracks(deezer_ctrl)
        
        date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
        dates = []
        for t in tracks:
            found = date_pattern.findall(t)
            if found:
                try:
                    dt = datetime.strptime(found[0], "%d/%m/%Y")
                    dates.append(dt)
                except: pass
                
        first_dt = None
        current_sort = 'inconnu'
        for dt in dates:
            if first_dt is None:
                first_dt = dt
            elif dt != first_dt:
                if first_dt < dt:
                    current_sort = 'asc'
                else:
                    current_sort = 'desc'
                break
                
        print(f"[DEEZER UIA] Tri détecté : {current_sort}")
        
        if current_sort in ('asc', 'inconnu'):
            print(f"[DEEZER UIA] Clic sur 'AJOUTÉ' pour trier en déchronologique...")
            try:
                pattern = btn.GetInvokePattern()
                if pattern:
                    pattern.Invoke()
                else:
                    btn.Click(simulateMove=False)
            except Exception as e:
                print(f"[DEEZER UIA] Échec Invoke, fallback Clic: {e}")
                btn.Click(simulateMove=False)
            time.sleep(1.0)
            return True
        else:
            print("[DEEZER UIA] La playlist est déjà triée par ajout déchronologique.")
            return False
    except Exception as e:
        print(f"[DEEZER UIA] Erreur lors du tri de la playlist : {e}")
        return False

def _trier_si_playlist(uri):
    if "playlist" not in uri.lower():
        return
    try:
        print(f"[DEEZER] Détection d'une playlist ({uri}), attente de chargement et tri...")
        t0 = time.time()
        deezer_ctrl = None
        while time.time() - t0 < 8:
            try:
                deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
                if deezer_ctrl.Exists(0.1):
                    header = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
                    if header.Exists(0.1):
                        break
            except:
                pass
            time.sleep(0.5)
            
        if deezer_ctrl:
            _sort_playlist_dechronologique(deezer_ctrl)
    except Exception as e:
        print(f"[DEEZER] Échec du tri automatique : {e}")

# Test on the active playlist
uri = "deezer://playlist/10487355742"
_trier_si_playlist(uri)
print("Test completed.")
