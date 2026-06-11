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

async def test_search(query, expected_in_title):
    print(f"\n=== Test: '{query}' ===")
    result = await deezer_rechercher(query)
    print(f"JARVIS réponse: {result}")
    
    # Wait for music to start and verify
    print("Waiting 8 seconds...")
    time.sleep(8)
    playing = deezer_obtenir_titre_encours()
    print(f"En écoute : {playing}")
    if playing:
        print(f"✅ SUCCÈS")
        return True
    else:
        print(f"❌ ÉCHEC : aucun titre détecté en cours de lecture")
        return False

async def main():
    results = []

    # Test 1 : joue moi l'album invincible de michael jackson
    ok1 = await test_search("joue moi l'album invincible de michael jackson", "Michael Jackson")
    results.append(("joue moi l'album invincible de michael jackson", ok1))

    # Kill deezer between tests
    print("\n--- Killing Deezer between tests ---")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'deezer.exe':
            try: proc.kill()
            except: pass
    time.sleep(2.0)

    # Test 2 : joue moi l'artiste michael jackson
    ok2 = await test_search("joue moi l'artiste michael jackson", "Michael Jackson")
    results.append(("joue moi l'artiste michael jackson", ok2))

    print("\n=== Résultats ===")
    for q, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} '{q}'")

asyncio.run(main())
