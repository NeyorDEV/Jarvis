import asyncio
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.deezer_controller import (
    deezer_rechercher,
    deezer_lecture_pause,
    deezer_suivant,
    deezer_precedent,
    deezer_stop,
    deezer_obtenir_titre_encours
)

async def test_scenario():
    print("🎬 DEBUT DU TEST DU CONTRÔLEUR DEEZER (UIA)")
    print("==========================================")
    
    # 1. Test de recherche d'une chanson
    recherche_chanson = "Get Lucky Daft Punk"
    print(f"\n🔍 Test 1 : Recherche chanson '{recherche_chanson}'...")
    res = await deezer_rechercher(recherche_chanson)
    print(f"👉 Résultat : {res}")
    
    await asyncio.sleep(6)
    meta = deezer_obtenir_titre_encours()
    print(f"🎵 En cours de lecture : {meta}")
    
    # 2. Test Pause/Play
    print("\n⏯ Test 2 : Pause...")
    res = await deezer_stop()
    print(f"👉 Résultat : {res}")
    
    await asyncio.sleep(3)
    
    print("\n⏯ Test 3 : Reprise...")
    res = await deezer_lecture_pause()
    print(f"👉 Résultat : {res}")
    
    await asyncio.sleep(3)
    
    # 3. Test de recherche d'un artiste
    recherche_artiste = "l'artiste Werenoi"
    print(f"\n🔍 Test 4 : Recherche artiste '{recherche_artiste}'...")
    res = await deezer_rechercher(recherche_artiste)
    print(f"👉 Résultat : {res}")
    
    await asyncio.sleep(6)
    meta = deezer_obtenir_titre_encours()
    print(f"🎵 En cours de lecture : {meta}")
    
    # 4. Test de recherche d'une playlist
    recherche_playlist = "la playlist Rap français"
    print(f"\n🔍 Test 5 : Recherche playlist '{recherche_playlist}'...")
    res = await deezer_rechercher(recherche_playlist)
    print(f"👉 Résultat : {res}")
    
    await asyncio.sleep(6)
    meta = deezer_obtenir_titre_encours()
    print(f"🎵 En cours de lecture : {meta}")
    
    print("\n🎉 Fin du scénario de test !")

if __name__ == "__main__":
    asyncio.run(test_scenario())
