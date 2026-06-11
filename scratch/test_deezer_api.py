import os
import requests
import json
import asyncio
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Charger le fichier .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)

async def get_deezer_api_token(arl):
    try:
        url = "https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&api_version=1.0&api_token="
        cookies = {"arl": arl}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = await asyncio.to_thread(requests.get, url, cookies=cookies, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("results", {}).get("checkForm")
            return token
    except Exception as e:
        print(f"Erreur token: {e}")
    return None

async def test_api():
    arl = os.getenv("DEEZER_ARL")
    if not arl:
        print("❌ Aucun DEEZER_ARL trouvé dans le fichier .env !")
        return
        
    print(f"🔑 ARL trouvé (début) : {arl[:15]}...")
    print("⚙ Récupération du token API...")
    token = await get_deezer_api_token(arl)
    if not token:
        print("❌ Impossible de récupérer le token API. Votre ARL est probablement invalide ou expiré !")
        return
        
    print(f"✔ Token API récupéré : {token}")
    
    print("🔎 Récupération de l'historique d'écoute...")
    try:
        url = f"https://www.deezer.com/ajax/gw-light.php?method=user.getHistory&api_version=1.0&api_token={token}"
        cookies = {"arl": arl}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = await asyncio.to_thread(requests.get, url, cookies=cookies, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tracks = data.get("results", {}).get("data", [])
            if tracks:
                print(f"✔ Historique récupéré ! Nombre de morceaux : {len(tracks)}")
                track = tracks[0]
                print(f"\nDernier morceau écouté/en cours :")
                print(f" - Titre : {track.get('SNG_TITLE')}")
                print(f" - Artiste : {track.get('ART_NAME')}")
                print(f" - Durée : {track.get('DURATION')} secondes")
                print(f" - ID : {track.get('SNG_ID')}")
            else:
                print("❌ Aucun historique d'écoute trouvé.")
        else:
            print(f"❌ Échec de la requête historique : Code {resp.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de la requête historique : {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
