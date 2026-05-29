import os
import json
import builtins

_LISTES_PATH = "jarvis_listes.json"

def _charger_listes():
    if os.path.exists(_LISTES_PATH):
        try:
            with open(_LISTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"courses": [], "notes": [], "todo": []}

def _sauvegarder_listes(data):
    try:
        with open(_LISTES_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except: pass

async def resoudre_listes_locales(texte):
    """Gère les listes de courses, notes et tâches localement."""
    t = texte.lower().strip()
    if "google" in t or "tasks" in t:
        return None
    data = _charger_listes()
    
    # 1. AJOUT
    if "ajoute" in t or "ajouter" in t or "mets" in t:
        cible = None
        if "course" in t: cible = "courses"
        elif "note" in t: cible = "notes"
        elif "tâche" in t or "todo" in t: cible = "todo"
        
        if cible:
            # Extraction de l'élément : on enlève le verbe et la destination
            item = t.replace("ajoute", "").replace("ajouter", "").replace("mets", "").replace("met", "")
            item = item.replace("sur ma liste de courses", "").replace("à ma liste de courses", "")
            item = item.replace("sur ma liste de notes", "").replace("à ma liste de notes", "")
            item = item.replace("sur ma liste de tâches", "").replace("à ma liste de tâches", "")
            item = item.replace("sur ma liste", "").replace("dans ma liste", "")
            item = item.replace('"', '').replace("  ", " ").strip()
            
            if item:
                data[cible].append(item.capitalize())
                _sauvegarder_listes(data)
                return f"C'est fait, j'ai ajouté {item} à votre liste de {cible}, Monsieur."

    # 2. LECTURE
    if "qu'est-ce qu'il y a" in t or "affiche" in t or "montre" in t or "lire" in t:
        if "course" in t:
            items = data.get("courses", [])
            if not items: return "Votre liste de courses est vide, Monsieur."
            return f"Voici votre liste de courses : {', '.join(items)}."
        elif "note" in t:
            items = data.get("notes", [])
            if not items: return "Vous n'avez aucune note enregistrée, Monsieur."
            return f"Voici vos notes : {', '.join(items)}."

    # 3. VIDAGE
    if "vide" in t or "supprime" in t or "efface" in t:
        if "course" in t:
            data["courses"] = []
            _sauvegarder_listes(data)
            return "La liste de courses a été vidée, Monsieur."

    return None

# Injection builtins
builtins.resoudre_listes_locales = resoudre_listes_locales
