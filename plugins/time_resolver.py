import builtins
import datetime
import pytz

_FUSEAUX = {
    "new york": "America/New_York",
    "london": "Europe/London", "londres": "Europe/London",
    "paris": "Europe/Paris", "berlin": "Europe/Berlin",
    "tokyo": "Asia/Tokyo", "sydney": "Australia/Sydney",
    "dubai": "Asia/Dubai", "moscou": "Europe/Moscow"
}

_MONNAIES = {
    "france": "Euro (€)", "etats-unis": "Dollar américain ($)",
    "japon": "Yen (¥)", "royaume-uni": "Livre sterling (£)"
}

async def resoudre_temps_localement(texte):
    """Gère l'heure mondiale et les infos monétaires."""
    t = texte.lower().strip()
    
    # HEURE
    if "heure à" in t or "heure au" in t or "heure en" in t:
        for ville, zone in _FUSEAUX.items():
            if ville in t:
                tz = pytz.timezone(zone)
                heure = datetime.datetime.now(tz).strftime("%H:%M")
                return f"Il est actuellement {heure} à {ville.capitalize()}, Monsieur."

    # MONNAIE
    if "monnaie" in t or "devise" in t:
        for pays, monnaie in _MONNAIES.items():
            if pays in t: return f"La monnaie utilisée en {pays.capitalize()} est le {monnaie}."

    return None

# Injection builtins
builtins.resoudre_temps_localement = resoudre_temps_localement
