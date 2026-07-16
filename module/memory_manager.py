import os
import json
import time
from google.genai import types

# MEMOIRE PERSISTANTE
# ==========================================
MEMOIRE_FILE = "jarvis_memoire.json"

def charger_memoire():
    if os.path.exists(MEMOIRE_FILE):
        try:
            with open(MEMOIRE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def sauvegarder_memoire(memoire):
    try:
        with open(MEMOIRE_FILE, "w", encoding="utf-8") as f:
            json.dump(memoire, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde memoire : {e}")

def ajouter_memoire(cle, valeur):
    memoire      = charger_memoire()
    memoire[cle] = {"valeur": valeur, "timestamp": time.strftime("%d/%m/%Y %H:%M")}
    sauvegarder_memoire(memoire)

def supprimer_memoire(cle):
    memoire = charger_memoire()
    if cle in memoire:
        del memoire[cle]
        sauvegarder_memoire(memoire)
        return True
    return False

def construire_contexte_memoire():
    memoire = charger_memoire()
    if not memoire:
        return ""
    lignes = ["MEMOIRE PERSISTANTE :"]
    for cle, data in memoire.items():
        lignes.append(f"  - {cle} : {data['valeur']} (note le {data['timestamp']})")
    return "\n".join(lignes)

# ==========================================
# HISTORIQUE CONVERSATIONS PERSISTANT
# ==========================================
HISTORIQUE_CONV_FILE = "jarvis_conversations.json"
MAX_ECHANGES_FICHIER = 200   # max échanges stockés sur disque
MAX_ECHANGES_CHARGE  = 30    # échanges rechargés au démarrage (contexte IA)

def _sauvegarder_echange_conv(user_text: str, model_text: str):
    """Ajoute un échange user/model au fichier JSON persistant."""
    try:
        echanges = []
        if os.path.exists(HISTORIQUE_CONV_FILE):
            with open(HISTORIQUE_CONV_FILE, "r", encoding="utf-8") as f:
                echanges = json.load(f)
        echanges.append({
            "date":  time.strftime("%d/%m/%Y"),
            "heure": time.strftime("%H:%M"),
            "user":  user_text[:2000],
            "model": model_text[:3000],
        })
        if len(echanges) > MAX_ECHANGES_FICHIER:
            echanges = echanges[-MAX_ECHANGES_FICHIER:]
        with open(HISTORIQUE_CONV_FILE, "w", encoding="utf-8") as f:
            json.dump(echanges, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CONV] Erreur sauvegarde historique: {e}")

def _charger_historique_recent():
    """Charge les derniers échanges et retourne une liste types.Content."""
    if not os.path.exists(HISTORIQUE_CONV_FILE):
        return []
    try:
        with open(HISTORIQUE_CONV_FILE, "r", encoding="utf-8") as f:
            echanges = json.load(f)
        recents = echanges[-MAX_ECHANGES_CHARGE:]
        hist = []
        for e in recents:
            date_str = f"[{e.get('date','?')} {e.get('heure','?')}] "
            hist.append(types.Content(role="user",  parts=[types.Part(text=date_str + e["user"])]))
            hist.append(types.Content(role="model", parts=[types.Part(text=e["model"])]))
        # print(f"[CONV] {len(recents)} echanges passes rechargees en memoire.")
        return hist
    except Exception as e:
        print(f"[CONV] Erreur chargement historique: {e}")
        return []

async def consolider_memoire_ia():
    """Analyse l'historique récent des conversations avec Gemini pour en extraire des faits marquants et mettre à jour la mémoire persistante."""
    import builtins
    from core.config import CHOSEN_MODEL
    
    # 1. Charger l'historique
    if not os.path.exists(HISTORIQUE_CONV_FILE):
        return False
    try:
        with open(HISTORIQUE_CONV_FILE, "r", encoding="utf-8") as f:
            echanges = json.load(f)
    except Exception:
        return False
        
    if not echanges:
        return False
        
    # Prendre les 30 derniers échanges pour la consolidation
    recents = echanges[-30:]
    
    # Formater les échanges
    conv_text = ""
    for e in recents:
        conv_text += f"[{e.get('date')} {e.get('heure')}] User: {e.get('user')}\nAssistant: {e.get('model')}\n\n"
        
    # Charger la mémoire actuelle
    memoire_actuelle = charger_memoire()
    mem_formatted = json.dumps(memoire_actuelle, ensure_ascii=False, indent=2)
    
    prompt = f"""Analyse l'historique récent des conversations ci-dessous pour extraire les faits persistants importants ou les préférences de l'utilisateur (mylane). 
Mets à jour ou ajoute les informations dans la mémoire. Ne conserve que les informations durables (goûts, outils préférés, prénoms de proches, choix technologiques) et ignore les détails transitoires (timers, météo d'aujourd'hui, requêtes système ponctuelles).

MÉMOIRE ACTUELLE :
{mem_formatted}

CONVERSATIONS RÉCENTES :
{conv_text}

Renvoie OBLIGATOIREMENT un objet JSON respectant ce format :
{{
  "updates": {{
    "clé": "valeur de l'information extraite avec son contexte"
  }},
  "deletes": ["clés devenues obsolètes ou fausses à supprimer"]
}}
Ne renvoie rien d'autre que le JSON brut. Si aucune nouvelle information n'est détectée, renvoie un objet vide pour updates et deletes.
"""

    print("[MEMORY MANAGER] Déclenchement de la consolidation de mémoire via Gemini...")
    try:
        client = getattr(builtins, "client", None)
        if not client:
            import google.genai as genai
            from core.config import GEMINI_API_KEY
            client = genai.Client(api_key=GEMINI_API_KEY)
            
        response = await client.aio.models.generate_content(
            model=CHOSEN_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        data = {}
        if response and response.text:
            try:
                data = json.loads(response.text)
            except Exception as je:
                print(f"[MEMORY MANAGER] Erreur lors du décodage du JSON de la réponse : {je}")
        
        updates = data.get("updates", {}) if isinstance(data, dict) else {}
        deletes = data.get("deletes", []) if isinstance(data, dict) else []
        
        if updates or deletes:
            mem = charger_memoire()
            timestamp = time.strftime("%d/%m/%Y %H:%M")
            for k, v in updates.items():
                mem[k] = {"valeur": v, "timestamp": timestamp}
                print(f"[MEMORY MANAGER] Fait mémorisé : {k} -> {v}")
            for k in deletes:
                if k in mem:
                    del mem[k]
                    print(f"[MEMORY MANAGER] Fait supprimé : {k}")
            sauvegarder_memoire(mem)
            return True
            
    except Exception as e:
        print(f"[MEMORY MANAGER] Erreur lors de la consolidation de mémoire : {e}")
        
    return False

# Injection builtins
import builtins
builtins.consolider_memoire_ia = consolider_memoire_ia

