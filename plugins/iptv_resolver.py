import builtins
import json
import asyncio

def nettoyer_accent(texte):
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

async def resoudre_iptv_localement(texte):
    t = nettoyer_accent(texte.lower().strip())
    
    mots_cles = [
        "ouvre le lecteur de video", "ouvre le lecteur video",
        "lance le lecteur video", "ouvre l'iptv", "lance l'iptv",
        "affiche l'iptv", "ouvre la tele", "ouvre le lecteur de films",
        "lance le lecteur de films", "ouvre le lecteur multimedia",
        "lance le lecteur multimedia"
    ]
    
    if any(k in t for k in mots_cles):
        print("[IPTV RESOLVER] Commande d'ouverture du lecteur IPTV reçue.")
        
        if hasattr(builtins, "CONNECTED_CLIENTS") and builtins.CONNECTED_CLIENTS:
            msg = json.dumps({"type": "iptv_open"})
            try:
                await asyncio.gather(*[ws.send(msg) for ws in builtins.CONNECTED_CLIENTS], return_exceptions=True)
            except Exception as e:
                print(f"[ERREUR WS] Broadcast iptv_open: {e}")
                
        return "Très bien, j'ouvre le lecteur vidéo et IPTV sur votre interface, mylane."
        
    return None

# Injection globale dynamique
builtins.resoudre_iptv_localement = resoudre_iptv_localement
