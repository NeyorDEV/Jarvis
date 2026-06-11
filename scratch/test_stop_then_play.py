"""
Test : approche page piste directe mais en stoppant la lecture d'abord
"""
import sys, os, asyncio, time, psutil, subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from controller.deezer_controller import (
    get_deezer_main_control, find_player_button, _clic_control,
    _ouvrir_uri_deezer, _uia_clic_bouton_page_dynamique,
    deezer_ouvrir, deezer_obtenir_titre_encours, _focus_deezer
)

DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

# ---- Simuler un contexte réaliste : une chanson différente joue déjà ----
# Kill + launch avec 1809 qui joue
print("Step 1: Lancement de Deezer avec 1809 en cours de lecture...")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try: proc.kill()
        except: pass
time.sleep(2.0)

subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/2070327887"], cwd=DEEZER_DIR, shell=False)
time.sleep(10)

# Cliquer play sur 1809 pour qu'il joue réellement
ctrl = get_deezer_main_control()
if ctrl:
    from controller.deezer_controller import find_page_play_button
    btn = find_page_play_button(ctrl, ["Écouter", "Reprendre"])
    if btn:
        _clic_control(btn)
        print("1809 lancé, en attente 3s...")
        time.sleep(3)
        print(f"En écoute : {deezer_obtenir_titre_encours()}")

# ---- Maintenant on essaie de lancer C63 via page piste DIRECTEMENT ----
print("\nStep 2: Tentative de jouer C63 via page piste directe (SANS stop préalable)...")
_ouvrir_uri_deezer("deezer://track/3045111091")
_uia_clic_bouton_page_dynamique(["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"], timeout=12, wait_for_title="C63")
time.sleep(5)
result1 = deezer_obtenir_titre_encours()
print(f"Résultat SANS stop : {result1}")

# ---- Même test mais EN STOPPANT D'ABORD ----
print("\nStep 3: Même chose mais on STOPPE la lecture avant de naviguer...")
# D'abord relancer 1809
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try: proc.kill()
        except: pass
time.sleep(2.0)
subprocess.Popen([DEEZER_EXE, "--force-renderer-accessibility", "deezer://track/2070327887"], cwd=DEEZER_DIR, shell=False)
time.sleep(10)
ctrl = get_deezer_main_control()
if ctrl:
    btn = find_page_play_button(ctrl, ["Écouter", "Reprendre"])
    if btn:
        _clic_control(btn)
        time.sleep(3)
        print(f"1809 joue : {deezer_obtenir_titre_encours()}")

# Maintenant on STOPPE avant de naviguer vers C63
print("Arrêt de la lecture...")
ctrl = get_deezer_main_control()
if ctrl:
    btn_pause = find_player_button(ctrl, ["Pause", "Mettre en pause"])
    if btn_pause:
        _clic_control(btn_pause)
        print("Lecture stoppée.")
        time.sleep(1.0)

# Naviguer vers C63
print("Navigation vers C63...")
_ouvrir_uri_deezer("deezer://track/3045111091")
_uia_clic_bouton_page_dynamique(["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"], timeout=12, wait_for_title="C63")
time.sleep(5)
result2 = deezer_obtenir_titre_encours()
print(f"Résultat AVEC stop : {result2}")

print("\n=== Résumé ===")
print(f"Sans stop préalable : {result1}")
print(f"Avec stop préalable : {result2}")
