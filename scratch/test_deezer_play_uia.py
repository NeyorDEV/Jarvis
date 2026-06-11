import subprocess
import os
import time
import sys
import uiautomation as auto

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def ensure_deezer_running_with_accessibility():
    # Vérifier si un processus Deezer tourne
    r = subprocess.run("tasklist /FI \"IMAGENAME eq Deezer.exe\"", shell=True, capture_output=True, text=True)
    if "Deezer.exe" not in r.stdout:
        print("🚀 Lancement de Deezer avec accessibilité...")
        deezer_dir = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"
        deezer_exe = os.path.join(deezer_dir, "Deezer.exe")
        subprocess.Popen(
            [deezer_exe, "--force-renderer-accessibility"],
            cwd=deezer_dir,
            shell=False
        )
        time.sleep(8)
    else:
        # Il tourne, mais on ne sait pas s'il a l'accessibilité.
        # Le script de test le verra vite.
        print("✔ Deezer tourne déjà.")

def get_currently_playing_track(deezer_ctrl):
    """Extrait le titre de la chanson en cours depuis le DocumentControl."""
    for child in deezer_ctrl.GetChildren():
        if child.ControlTypeName == "DocumentControl":
            title = child.Name
            # Le titre est sous la forme : "Chanson - Artiste - Deezer"
            if title and " - Deezer" in title:
                song_info = title.replace(" - Deezer", "").strip()
                return song_info
    return "Aucune lecture détectée"

def find_player_button(deezer_ctrl, button_names):
    """Recherche récursivement un bouton ayant l'un des noms spécifiés et faisant partie de la barre de contrôle."""
    # La barre de contrôle contient généralement 'Suivant' et 'Précédent'
    # On peut faire une recherche de tous les boutons
    buttons = []
    
    def _collect_buttons(control):
        if control.ControlTypeName == "ButtonControl":
            name = control.Name or ""
            if name in button_names or any(b in name for b in button_names) or control.AutomationId == "player-play":
                buttons.append(control)
        for child in control.GetChildren():
            _collect_buttons(child)
            
    _collect_buttons(deezer_ctrl)
    
    # Filtrer pour trouver celui de la barre de lecture principale
    # Le bouton principal est souvent entouré des boutons 'Précédent'/'Suivant'
    for btn in buttons:
        # On peut remonter au parent et vérifier s'il a 'Suivant' ou 'Précédent' comme enfant
        parent = btn.GetParentControl()
        if parent:
            sibling_names = [c.Name for c in parent.GetChildren() if c.ControlTypeName == "ButtonControl"]
            if "Suivant" in sibling_names or "Précédent" in sibling_names:
                return btn
                
    # Fallback sur le premier bouton trouvé
    if buttons:
        return buttons[0]
    return None

def test_control():
    ensure_deezer_running_with_accessibility()
    
    print("🔍 Recherche de la fenêtre Deezer...")
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(2.0):
        print("❌ Impossible de trouver la fenêtre Deezer.")
        return
        
    print(f"✔ Fenêtre trouvée : HWND {deezer_ctrl.NativeWindowHandle}")
    
    # 1. Lire la musique en cours
    track = get_currently_playing_track(deezer_ctrl)
    print(f"🎵 En cours de lecture : {track}")
    
    # 2. Trouver le bouton Play/Pause
    # En français, les boutons peuvent être nommés 'Écouter' (Play) ou 'Pause' / 'Mettre en pause'
    play_pause_names = ["Écouter", "Pause", "Mettre en pause"]
    btn_play = find_player_button(deezer_ctrl, play_pause_names)
    
    if btn_play:
        print(f"✔ Bouton Play/Pause trouvé : Name='{btn_play.Name}'")
        # Simuler un clic sur le bouton
        print("🖱 Clic sur le bouton Play/Pause...")
        btn_play.Click()
        time.sleep(3)
        
        # Mettre à jour l'info
        track = get_currently_playing_track(deezer_ctrl)
        print(f"🎵 Après clic : {track}")
    else:
        print("❌ Bouton Play/Pause introuvable.")

if __name__ == "__main__":
    test_control()
