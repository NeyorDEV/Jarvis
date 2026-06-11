"""
Teste que la stratégie actuelle :
1) Joue le bon titre (via page album)
2) Affiche bien la page piste après
"""
import sys, os, asyncio, time, psutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from controller.deezer_controller import deezer_rechercher, deezer_obtenir_titre_encours
import pyautogui

# Kill Deezer
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try: proc.kill()
        except: pass
time.sleep(2.0)

DEST = r"C:\Users\mylan\.gemini\antigravity\brain\87b26e30-c877-4d90-89c9-39a5645c2eec"

async def main():
    print("=== Test: joue c63 de werenoi ===")
    result = await deezer_rechercher("c63 de werenoi")
    print(f"JARVIS: {result}")
    # Attendre un peu que la page piste se charge
    time.sleep(4)
    playing = deezer_obtenir_titre_encours()
    print(f"En écoute : {playing}")
    # Screenshot pour voir la page affichée
    shot = pyautogui.screenshot()
    shot.save(os.path.join(DEST, "test_page_piste_c63.png"))
    print("Screenshot sauvegardé.")

asyncio.run(main())
