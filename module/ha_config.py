# ============================================================
#  ha_config.py — Configuration Home Assistant & Météo
#  Personnalisez CE fichier selon votre installation domotique
#  Ne touchez pas main2.py pour la domotique, tout est ici.
# ============================================================

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Connexion Home Assistant (chargé depuis .env) ────────────
HA_URL    = os.getenv("HA_URL", "")
HA_TOKEN  = os.getenv("HA_TOKEN", "")
HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type" : "application/json"
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 1 — MÉTÉO PAR DÉFAUT
#  Remplacez par votre ville et ses coordonnées GPS.
#  Coordonnées : https://www.latlong.net/
# ═══════════════════════════════════════════════════════════════
VILLE_PAR_DEFAUT = "Monistrol-sur-Loire"   # ← Votre ville
LAT_PAR_DEFAUT   = 45.2917                 # ← Latitude
LON_PAR_DEFAUT   = 4.1722                  # ← Longitude

# ═══════════════════════════════════════════════════════════════
#  SECTION 2 — LUMIÈRES
#  Format : "nom vocal" : "entity_id Home Assistant"
#  Pour trouver un entity_id : HA → Paramètres → Appareils
#    → cliquez sur l'entité → "Informations sur l'entité"
# ═══════════════════════════════════════════════════════════════
PIECES_LUMIERES = {
    # Salon
    "salon"            : "light.salon",
    "plafond salon"    : "light.plafond",
    "canapes"          : "light.canapes",
    "lampadaire"       : "light.lampadaire",
    "lampe de chevet"  : "light.lampe_de_chevet_2",
    "grosse boule"     : "light.grosse_boule",
    "petite boule"     : "light.petite_boule",

    # Cuisine
    "cuisine"          : "light.lsc_smart_led_strip_rgbic_cctic_5m",
    "cuisine 2"        : "light.cuisine_2",

    # Bureau
    "bureau"           : "light.bureau",
    "pc"               : "light.pc",
    "pc 2"             : "light.pc_2",

    # Parents
    "parents"          : "light.chambre_parentale",
    "chambre parentale": "light.chambre_parentale",
    "chambre"          : "light.chambre_parentale",
    "plafond chambre"  : "light.plafond_2",

    # Globaux
    "toutes"           : "light.all",
    "tout"             : "light.all",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 3 — PRISES CONNECTÉES
#  Format : "nom vocal" : "entity_id switch.xxx"
# ═══════════════════════════════════════════════════════════════
PIECES_PRISES = {
    "salon"   : "switch.prise_salon",
    "bureau"  : "switch.prise_bureau",
    "cuisine" : "switch.prise_cuisine",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 4 — CAPTEURS TEMPÉRATURE & DIVERS
#  Format : "nom vocal" : "entity_id sensor.xxx"
#  Vous pouvez ajouter autant de pièces que nécessaire.
# ═══════════════════════════════════════════════════════════════
PIECES_CAPTEURS = {
    "salon"        : "sensor.salon_temperature_2",
    "chambre"      : "sensor.miaomiaoc_de_blt_4_14kc52pmcgk00_t2_temperature_p_2_1",
    "bureau"       : "sensor.temp_temperature",
    "exterieur"    : "sensor.temperature_exterieure",
    "dehors"       : "sensor.temperature_exterieure",
    "consommation" : "sensor.lixee_zlinky_tic_puissance_apparente",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 5 — CAPTEURS HUMIDITÉ
#  Format : "nom vocal" : "entity_id sensor.xxx"
# ═══════════════════════════════════════════════════════════════
PIECES_HUMIDITE = {
    "bureau" : "sensor.temp_humidite",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 6 — TARIFS ÉLECTRICITÉ (€/kWh)
#  Adaptez selon votre contrat EDF / fournisseur
#  p1-p6 = plages tarifaires Linky (heures creuses, pleines, etc.)
# ═══════════════════════════════════════════════════════════════
HA_TARIFS = {
    "p1": 0.1296,
    "p2": 0.1603,
    "p3": 0.1486,
    "p4": 0.1894,
    "p5": 0.1568,
    "p6": 0.7562,
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 7 — SUIVI ÉNERGIE PAR APPAREIL
#  Format : "nom vocal" : "entity_id sensor.xxx_mensuel"
# ═══════════════════════════════════════════════════════════════
APPAREILS_ENERGIE = {
    "tv"             : "sensor.prise_1_salon_mensuel",
    "salon"          : "sensor.prise_1_salon_mensuel",
    "voiture"        : "sensor.zoe_mensuel",
    "lave-vaisselle" : "sensor.prise_2_lave_vaisselle_mensuel",
    "pc salon"       : "sensor.pc_salon_conso_pc_salon_mensuel_2",
    "bureau"         : "sensor.bureau_mensuel",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 8 — BATTERIES DES APPAREILS
#  Format : "nom vocal" : "entity_id sensor.xxx_battery_level"
# ═══════════════════════════════════════════════════════════════
APPAREILS_BATTERIE = {
    "mon telephone"      : "sensor.sm_s921b_battery_level",
    "papa"               : "sensor.sm_s921b_battery_level",
    "samsung papa"       : "sensor.sm_s921b_battery_level",
    "maman"              : "sensor.sm_julie_battery_level",
    "iphone maman"      : "sensor.sm_julie_battery_level",
    "interrupteur"       : "sensor.maison_interrupteur_batterie",
    "toner"              : "sensor.samsung_m2020_series_black_toner_s_n_crum_17091625519",
    "imprimante"         : "sensor.samsung_m2020_series_black_toner_s_n_crum_17091625519",
    "detecteur cuisine"  : "sensor.detecteur_1_batterie",
    "detecteur escalier" : "sensor.detecteur_2_batterie",
    "thermometre bureau" : "sensor.temp_batterie",
}

# ═══════════════════════════════════════════════════════════════
#  SECTION 9 — COULEURS RGB
#  Format : "nom vocal" : [R, G, B]
#  Vous pouvez ajouter vos propres couleurs.
# ═══════════════════════════════════════════════════════════════
COULEURS_MAP = {
    "rouge"     : [255, 0,   0  ],
    "bleu"      : [0,   0,   255],
    "vert"      : [0,   255, 0  ],
    "blanc"     : [255, 255, 255],
    "orange"    : [255, 140, 0  ],
    "violet"    : [148, 0,   211],
    "rose"      : [255, 20,  147],
    "jaune"     : [255, 255, 0  ],
    "cyan"      : [0,   255, 255],
    "magenta"   : [255, 0,   255],
    "turquoise" : [64,  224, 208],
    "or"        : [255, 215, 0  ],
    "argent"    : [192, 192, 192],
    "indigo"    : [75,  0,   130],
    "marron"    : [139, 69,  19 ],
    "citron"    : [255, 250, 0  ],
    "corail"    : [255, 127, 80 ],
    "lavande"   : [230, 230, 250],
}

# ── Codes météo Open-Meteo (ne pas modifier) ─────────────────
CODES_METEO = {
    0:  "ciel degage",
    1:  "principalement clair", 2: "partiellement nuageux", 3: "couvert",
    45: "brouillard", 48: "brouillard givrant",
    51: "bruine legere", 53: "bruine moderee", 55: "bruine dense",
    61: "pluie faible", 63: "pluie moderee", 65: "pluie forte",
    71: "neige faible", 73: "neige moderee", 75: "neige forte",
    80: "averses faibles", 81: "averses moderees", 82: "averses violentes",
    85: "averses de neige", 86: "averses de neige fortes",
    95: "orage", 96: "orage avec grele", 99: "orage violent avec grele",
}

# ════════════════════════════════════════════════════════════════
#  FONCTIONS API HOME ASSISTANT
#  Ne modifiez pas ces fonctions — elles appellent l'API HA.
# ════════════════════════════════════════════════════════════════

def ha_appeler_service(domaine, service, entity_id, donnees=None):
    try:
        payload = {"entity_id": entity_id}
        if donnees:
            payload.update(donnees)
        print(f"[HA DEBUG] Calling {domaine}/{service} for {entity_id} with {donnees}")
        r = requests.post(
            f"{HA_URL}/api/services/{domaine}/{service}",
            headers=HA_HEADERS, json=payload, timeout=5
        )
        print(f"[HA DEBUG] Response {r.status_code}: {r.text}")
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"[HA] Erreur service : {e}")
        return False

def ha_get_etat(entity_id, attribut=None):
    try:
        r    = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HA_HEADERS, timeout=5)
        data = r.json()
        if attribut:
            return data.get("attributes", {}).get(attribut, "inconnu")
        return data.get("state", "inconnu")
    except Exception as e:
        print(f"[HA] Erreur get etat : {e}")
        return "inconnu"

def ha_get_calendrier(entity_id):
    try:
        now   = datetime.now()
        start = now.strftime("%Y-%m-%dT00:00:00Z")
        end   = now.strftime("%Y-%m-%dT23:59:59Z")
        r = requests.get(
            f"{HA_URL}/api/calendars/{entity_id}",
            headers=HA_HEADERS,
            params={"start": start, "end": end},
            timeout=5
        )
        return r.json()
    except Exception as e:
        print(f"[HA] Erreur calendrier : {e}")
        return []

def ha_lumiere(entity_id, etat="on", luminosite=None, rgb=None):
    service_name = "toggle" if etat == "toggle" else ("turn_on" if etat == "on" else "turn_off")
    donnees = {}
    if etat == "on":
        if luminosite is not None:
            donnees["brightness"] = int(luminosite)
        if rgb is not None:
            donnees["rgb_color"] = rgb
    return ha_appeler_service("light", service_name, entity_id, donnees)

def ha_interrupteur(entity_id, etat="on"):
    service_name = "turn_on" if etat == "on" else "turn_off"
    return ha_appeler_service("switch", service_name, entity_id)

def ha_thermostat(entity_id, temperature):
    return ha_appeler_service("climate", "set_temperature", entity_id, {"temperature": temperature})

def ha_scene(scene_id):
    return ha_appeler_service("scene", "turn_on", scene_id)

def ha_verrou(entity_id, etat="lock"):
    service_name = "lock" if etat == "lock" else "unlock"
    return ha_appeler_service("lock", service_name, entity_id)

# ════════════════════════════════════════════════════════════════
#  FONCTIONS MÉTÉO
#  Utilisent Open-Meteo (gratuit) + Home Assistant en fallback.
# ════════════════════════════════════════════════════════════════

OPEN_METEO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def geocoder_ville(ville):
    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ville, "count": 1, "language": "fr", "format": "json"},
            headers=OPEN_METEO_HEADERS,
            timeout=5
        )
        data = r.json()
        if data.get("results"):
            res = data["results"][0]
            return res["latitude"], res["longitude"], res.get("name", ville), res.get("country", "")
    except Exception as e:
        print(f"[METEO] Erreur geocoding : {e}")
    return None, None, ville, ""

def get_meteo_fallback_wttr_sync(city_name):
    try:
        url = f"https://wttr.in/{requests.utils.quote(city_name)}?format=j1"
        resp = requests.get(url, headers=OPEN_METEO_HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current_condition", [{}])[0]
            desc = curr.get("weatherDesc", [{}])[0].get("value", "Inconnu")
            translations = {
                "sunny": "ciel degage", "clear": "ciel degage", "partly cloudy": "partiellement nuageux",
                "cloudy": "nuageux", "overcast": "couvert", "mist": "brouillard", "fog": "brouillard",
                "patchy rain possible": "pluie faible", "patchy snow possible": "neige faible",
                "heavy rain": "pluie forte", "light rain": "pluie faible", "thunderstorm": "orage"
            }
            desc_fr = translations.get(desc.lower(), desc.lower())
            temp = round(float(curr.get("temp_C", 0)))
            return f"À {city_name}, il fait {temp} degrés et le ciel est {desc_fr}. C'est tout."
    except:
        pass
    return None

def get_meteo_actuelle(ville=None):
    try:
        nom_ville = ville or VILLE_PAR_DEFAUT
        lat, lon, nom_affiche, pays = geocoder_ville(nom_ville)
        if lat is None:
            lat, lon = LAT_PAR_DEFAUT, LON_PAR_DEFAUT
            nom_affiche = VILLE_PAR_DEFAUT
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude"       : lat, "longitude": lon,
                "current"        : "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weathercode,precipitation",
                "hourly"         : "temperature_2m,precipitation_probability",
                "daily"          : "temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,wind_speed_10m_max,sunrise,sunset",
                "timezone"       : "Europe/Paris",
                "forecast_days"  : 3,
                "wind_speed_unit": "kmh",
            },
            headers=OPEN_METEO_HEADERS,
            timeout=5
        )
        data = r.json()
        cur  = data["current"]
        code = cur.get("weathercode", 0)
        desc = CODES_METEO.get(code, "conditions inconnues")
        temp = round(float(cur.get("temperature_2m", 0)))
        return f"À {nom_affiche}, il fait {temp} degrés et le ciel est {desc}. C'est tout."
    except Exception:
        # Repli silencieux sur wttr.in si Open-Meteo est KO
        wttr_res = get_meteo_fallback_wttr_sync(nom_ville)
        if wttr_res:
            return wttr_res
        return "Je n'arrive pas à récupérer la météo pour le moment."

def get_meteo_ha():
    """Lit la météo depuis Home Assistant. Fallback quand Gemini est KO."""
    try:
        r = requests.get(f"{HA_URL}/api/states/weather.forecast_amilly", headers=HA_HEADERS, timeout=5)
        data = r.json()
        etat  = data.get("state", "inconnu")
        attrs = data.get("attributes", {})
        temp     = attrs.get("temperature", "?")
        humidite = attrs.get("humidity", None)
        vent     = attrs.get("wind_speed", None)
        etats_fr = {
            "sunny"          : "ensoleillé",
            "clear-night"    : "clair",
            "partlycloudy"   : "partiellement nuageux",
            "cloudy"         : "nuageux",
            "rainy"          : "pluvieux",
            "pouring"        : "forte pluie",
            "snowy"          : "neigeux",
            "snowy-rainy"    : "pluie et neige mêlées",
            "windy"          : "venteux",
            "windy-variant"  : "très venteux",
            "fog"            : "brumeux",
            "hail"           : "grêle",
            "lightning"      : "orageux",
            "lightning-rainy": "orage et pluie",
            "exceptional"    : "conditions exceptionnelles",
        }
        desc    = etats_fr.get(etat, etat)
        reponse = f"À {VILLE_PAR_DEFAUT}, il fait {temp} degrés et le ciel est {desc}"
        if humidite:
            reponse += f", humidité à {humidite}%"
        if vent:
            reponse += f", vent à {vent} km/h"
        reponse += ", mylane."
        return reponse
    except Exception as e:
        print(f"[METEO HA] Erreur : {e}")
        return None

def get_alertes_meteo(ville=None):
    try:
        nom_ville = ville or VILLE_PAR_DEFAUT
        lat, lon, nom_affiche, _ = geocoder_ville(nom_ville)
        if lat is None:
            lat, lon, nom_affiche = LAT_PAR_DEFAUT, LON_PAR_DEFAUT, VILLE_PAR_DEFAUT
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily"   : "weathercode,precipitation_sum,wind_speed_10m_max",
                "timezone": "Europe/Paris", "forecast_days": 3,
            },
            headers=OPEN_METEO_HEADERS,
            timeout=8
        )
        data    = r.json()
        daily   = data["daily"]
        alertes = []
        for i in range(len(daily["weathercode"])):
            code  = daily["weathercode"][i]
            pluie = daily.get("precipitation_sum", [0]*3)[i] or 0
            vent  = daily.get("wind_speed_10m_max", [0]*3)[i] or 0
            jour  = ["aujourd hui", "demain", "apres-demain"][i]
            if code in [95, 96, 99]:
                alertes.append(f"Orage prevu {jour}")
            if code in [71, 73, 75, 85, 86]:
                alertes.append(f"Neige prevue {jour}")
            if pluie > 20:
                alertes.append(f"Fortes pluies {jour} ({pluie}mm)")
            if vent > 60:
                alertes.append(f"Vents forts {jour} ({vent} km/h)")
        if alertes:
            return f"Alertes meteo pour {nom_affiche} : " + ", ".join(alertes) + "."
        return f"Aucune alerte meteo pour {nom_affiche} dans les 3 prochains jours."
    except Exception as e:
        return f"Impossible de verifier les alertes meteo : {e}"

def _charger_custom_ha_entities():
    """Charge les entités personnalisées Home Assistant depuis jarvis_config.json."""
    import json
    global PIECES_LUMIERES, PIECES_PRISES, PIECES_CAPTEURS
    try:
        _dir = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_dir) if os.path.basename(_dir) == "module" else _dir
        path = os.path.join(_root, "jarvis_config.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                
                # Charger les lumières custom
                custom_lights = cfg.get("custom_lights", [])
                for x in custom_lights:
                    PIECES_LUMIERES[x["name"].lower()] = x["entity_id"]
                    
                # Charger les prises custom
                custom_prises = cfg.get("custom_prises", [])
                for x in custom_prises:
                    PIECES_PRISES[x["name"].lower()] = x["entity_id"]
                    
                # Charger les capteurs custom
                custom_capteurs = cfg.get("custom_capteurs", [])
                for x in custom_capteurs:
                    PIECES_CAPTEURS[x["name"].lower()] = x["entity_id"]
                    
                # print(f"[HA CONFIG] Loaded custom entities: {len(custom_lights)} lights, {len(custom_prises)} plugs, {len(custom_capteurs)} sensors.")
                pass
    except Exception as e:
        print(f"[HA CONFIG] Error loading custom entities: {e}")

# Charger au démarrage
_charger_custom_ha_entities()
