import builtins
import subprocess
import time
import os
import re
import asyncio

# On importe les fonctions du fichier existant si possible
try:
    from controller.app_launcher import _APPS_CATALOGUE, _boulot_lancer, mode_boulot, mode_gaming, mode_rocket_league
except ImportError:
    _APPS_CATALOGUE = {}

async def resoudre_apps_localement(texte):
    """Gère l'ouverture et la fermeture des applications PC et les modes de travail/jeu."""
    t = texte.lower().strip()
    
    # S'il s'agit d'une commande complexe avec des enchaînements ou des actions DOM/saisie,
    # on renvoie None pour laisser le "cerveau" IA (LLM) s'en occuper de façon autonome.
    if any(k in t for k in ["saisis", "clique", "tape", "ecris", "remplace", "dans la", "barre de", " et ", " puis "]):
        return None
        
    # 1. GESTION DES MODES
    if any(k in t for k in ["mode boulot", "mode travail", "espace de travail"]):
        return await mode_boulot()
    if any(k in t for k in ["mode gaming", "mode jeu", "lance un jeu"]):
        return await mode_gaming()
    if any(k in t for k in ["mode rocket league", "lance rocket league"]):
        return await mode_rocket_league()

    # 2. OUVERTURE D'APPLICATIONS (Via Catalogue)
    if any(k in t for k in ["ouvre", "lance", "demarre"]):
        for app_key, data in _APPS_CATALOGUE.items():
            if app_key in t:
                success = _boulot_lancer(data["label"], data["noms"], data.get("hints"))
                if success: return f"J'ai lancé {data['label']} pour vous, mylane."
                return f"Je n'ai pas pu localiser {data['label']} sur votre système."

    # 3. MUSIQUE DYNAMIQUE (Depuis Paramètres ou "mets de la musique")
    if "musique" in t and any(k in t for k in ["mets", "joue", "lance", "écoute", "ecoute", "play", "active", "démarre", "demarre"]):
        import webbrowser
        try:
            import pyautogui
        except ImportError:
            pyautogui = None
            
        import json as _j
        lien_perso = ""
        try:
            _p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarvis_config.json")
            with open(_p, "r", encoding="utf-8") as _f:
                lien_perso = _j.load(_f).get("musique_lien", "").strip()
        except: pass
        
        user_n = getattr(builtins, 'USER_NAME', 'mylane')
        
        if "youtube" in t or (lien_perso and "youtube.com" in lien_perso):
            url = lien_perso if lien_perso else "https://www.youtube.com/watch?v=Cr8K88UcO0s"
            webbrowser.open(url, new=2)
            if pyautogui:
                asyncio.create_task(asyncio.sleep(5)).add_done_callback(lambda _: pyautogui.press('f'))
            return f"C'est parti {user_n}, je lance votre musique sur YouTube."
        elif lien_perso:
            webbrowser.open(lien_perso, new=2)
            return f"C'est parti {user_n}, je lance votre musique personnalisée."
        elif "deezer" in t:
            try:
                subprocess.Popen(["explorer", "deezer:"], shell=False)
                return f"C'est parti {user_n}, j'ouvre votre musique sur Deezer."
            except: pass
        else:
            try:
                subprocess.Popen(["explorer", "spotify:"], shell=False)
                return f"C'est parti {user_n}, je lance votre playlist sur Spotify."
            except: pass

    # 4. ACTIONS SYSTÈME RAPIDES
    if any(k in t for k in ["explorateur", "mes dossiers", "mes fichiers"]):
        subprocess.Popen(["explorer.exe"])
        return "Explorateur de fichiers ouvert, Monsieur."
    if any(k in t for k in ["notepad", "bloc-notes", "note rapide"]):
        subprocess.Popen(["notepad.exe"])
        return "Bloc-notes ouvert pour vos notes, Monsieur."

    return None

# Injection builtins
builtins.resoudre_apps_localement = resoudre_apps_localement
