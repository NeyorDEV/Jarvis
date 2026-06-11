"""
Test d'intégration final - simule les commandes JARVIS réelles.
Teste les deux tracks problématiques : "1809 de menace santana" et "c63 de werenoi"
"""
import sys
import os
import asyncio
import time
import psutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from controller.deezer_controller import deezer_rechercher, deezer_obtenir_titre_encours

# Kill Deezer
print("=== Killing Deezer... ===")
for proc in psutil.process_iter(['name']):
    if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
        try: proc.kill()
        except: pass
time.sleep(2.0)

async def test_track(query, expected_title):
    print(f"\n=== Test: '{query}' ===")
    result = await deezer_rechercher(query)
    print(f"JARVIS réponse: {result}")
    time.sleep(6)
    playing = deezer_obtenir_titre_encours()
    print(f"En écoute : {playing}")
    if playing and expected_title.lower() in playing.get("title", "").lower():
        print(f"✅ SUCCÈS")
        return True
    else:
        print(f"❌ ÉCHEC : attendu '{expected_title}', obtenu '{playing}'")
        return False

async def main():
    results = []

    # Test 1 : 1809 de menace Santana
    ok1 = await test_track("1809 de menace santana", "1809")
    results.append(("1809 de menace santana", ok1))

    # Kill deezer between tests
    print("\n--- Killing Deezer between tests ---")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try: proc.kill()
            except: pass
    time.sleep(2.0)

    # Test 2 : C63 de Werenoi
    ok2 = await test_track("c63 de werenoi", "C63")
    results.append(("c63 de werenoi", ok2))

    # Kill deezer between tests
    print("\n--- Killing Deezer between tests ---")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try: proc.kill()
            except: pass
    time.sleep(2.0)

    # Test 3 : joue moi c63 de werenoi (with filler words)
    ok3 = await test_track("joue moi c63 de werenoi", "C63")
    results.append(("joue moi c63 de werenoi", ok3))

    print("\n=== Résultats ===")
    for query, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} '{query}'")

asyncio.run(main())
