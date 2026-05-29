import requests
import urllib.parse
import os
import time

def generer_image_ia(prompt):
    """
    Génère une image via l'API Pollinations.ai.
    Retourne l'URL de l'image générée.
    """
    try:
        print(f"[IMAGE] Génération pour : {prompt}")
        
        # Encodage du prompt pour l'URL
        prompt_enc = urllib.parse.quote(prompt)
        
        # Nouvelle API Pollinations
        seed = int(time.time())
        image_url = f"https://image.pollinations.ai/prompt/{prompt_enc}?seed={seed}&nologo=true"
        
        # On déguise la requête en navigateur web pour ne pas être bloqué/ralenti
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/jpeg, image/png, image/*"
        }
        
        # On télécharge l'image directement depuis le serveur Python (Timeout allongé à 45s)
        response = requests.get(image_url, headers=headers, timeout=45)
        if response.status_code == 200:
            import base64
            # On convertit l'image en base64 pour l'envoyer au WebSocket sans problème de CORS
            img_b64 = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{img_b64}"
        else:
            print(f"[IMAGE ERROR] Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[IMAGE ERROR] {e}")
        return None
