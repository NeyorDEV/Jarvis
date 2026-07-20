import json
import builtins
import asyncio

async def resoudre_globe_localement(texte):
    """Gère la navigation et le zoom sur le globe 3D avec forçage du mode d'affichage."""
    t = texte.lower().strip()
    bypass_terms = [
        # Internet & recherche générale
        "google", "internet", "web", "recherche", "rechercher",
        # Sports
        "sport", "psg", "match", "foot", "football", "score", "classement", "résumé", "resume",
        # Google Workspace
        "tasks", "tâche", "tache", "drive",
        # E-commerce & prix (€ ou mot "euro/euros" → intention achat, pas géo)
        "€", "euro", "euros", "moins de", "moins cher", "prix", "achat", "acheter",
        "amazon", "leboncoin", "fnac", "cdiscount", "vinted", "aliexpress", "ebay",
        "zalando", "booking", "airbnb", "kayak", "skyscanner", "blablacar",
        "ps5", "ps4", "xbox", "nintendo", "iphone", "samsung", "pc ", "laptop",
        # Shopping & produits
        "produit", "article", "annonce", "offre", "vente", "achat",
        # Navigation web explicite
        "sur leboncoin", "sur amazon", "sur booking", "sur zalando", "sur kayak",
        "sur google", "sur youtube", "sur le site",
    ]
    if any(term in t for term in bypass_terms):
        return None
        
    send_globe = getattr(builtins, "send_globe_command", None)
    
    if not send_globe: return None

    # 1. GESTION DU ZOOM
    if any(m in t for m in ["zoom", "rapproche", "plus près", "plus pres"]):
        asyncio.create_task(send_globe(globe_action="zoom_in"))
        return "Je zoome sur la zone, Monsieur."
    
    if any(m in t for m in ["dézoom", "dezoom", "éloigne", "eloigne", "plus loin"]):
        asyncio.create_task(send_globe(globe_action="zoom_out"))
        return "Je prends de la hauteur, Monsieur."

    # 2. GESTION DE LA NAVIGATION
    # Garde d'exclusion pour éviter de détourner les commandes du HUD, DOM, musique ou lumières
    elements_hud = ["clavier", "sous-titre", "parametre", "paramètre", "reglage", "réglage", "config", "meteo", "météo", "temperature", "température", "gpu", "lumiere", "lumière", "prise", "recette", "musique", "volume", "saisis", "clique", "tape", "ecris", "remplace", "barre de", " et ", " puis ", "recherche"]
    if any(e in t for e in elements_hud):
        return None

    declencheurs = ["montre-moi", "montre moi", "montre", "affiche", "va à", "vol vers", "direction", "cherche"]
    if any(m in t for m in declencheurs):
        lieu = t
        for m in declencheurs:
            if m in lieu: lieu = lieu.replace(m, "")
        lieu = lieu.replace("?", "").strip().capitalize()
        
        if not lieu or len(lieu) < 2: return None

        # GÉOCODAGE
        geocode = getattr(builtins, "geocode_lieu", None)
        lat, lon, nom_complet = None, None, lieu
        if geocode:
            lat, lon, nom_complet = await geocode(lieu)
            print(f"[DEBUG GLOBE] Destination: {nom_complet} | Lat: {lat} | Lon: {lon}")
        
        try:
            if lat and lon:
                # FORCE LE MODE GLOBE 3D AVANT LE VOL
                asyncio.create_task(send_globe(globe_action="show_earth"))
                
                # Attente minime pour laisser l'interface switcher
                await asyncio.sleep(0.5)
                
                # ENVOI DU VOL
                asyncio.create_task(send_globe(
                    globe_action="fly_to", 
                    location=nom_complet, 
                    lat=lat, 
                    lon=lon
                ))
                return f"Bien sûr Monsieur, cap sur {lieu}. Initialisation du vol orbital."
            else:
                asyncio.create_task(send_globe(globe_action="fly_to", location=lieu))
                return f"Cap sur {lieu}, Monsieur. Je tente une localisation."
        except Exception as e:
            print(f"[GLOBE ERROR] {e}")
                
    return None

# Injection builtins
builtins.resoudre_globe_localement = resoudre_globe_localement
