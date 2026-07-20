import os
import time
import asyncio
import random
import re
import requests
import builtins
from wakeonlan import send_magic_packet
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner as sign_with_rsa_key
from adb_shell.auth.keygen import keygen

# --- CONFIGURATION (Philips 43PUS7906/12) ---
TV_NAME = "43PUS7906/12"
TV_IP   = "192.168.0.151"
TV_MAC  = "24-b7-2a-74-97-db"
ADB_KEY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "adb_key")

def get_adb_signer():
    """Génère ou récupère la clé de signature ADB."""
    if not os.path.exists(ADB_KEY_PATH):
        keygen(ADB_KEY_PATH)
    with open(ADB_KEY_PATH) as f:
        priv = f.read()
    with open(ADB_KEY_PATH + ".pub") as f:
        pub = f.read()
    return sign_with_rsa_key(pub, priv)

async def adb_command(cmd_shell):
    """Exécute une commande shell ADB sur la télé."""
    try:
        signer = get_adb_signer()
        device = AdbDeviceTcp(TV_IP, 5555, default_transport_timeout_s=3)
        device.connect(rsa_keys=[signer], auth_timeout_s=3)
        res = device.shell(cmd_shell)
        device.close()
        return True
    except Exception:
        return False

# --- LOGIQUE TECHNIQUE ---

async def tv_allumer():
    for port in [7, 9]:
        send_magic_packet(TV_MAC, ip_address="192.168.0.255", port=port)
    await asyncio.sleep(2)
    if await adb_command("input keyevent 224"):
        await adb_command("input keyevent 3")
        return "J'ai allumé votre télé, mylane."
    return "J'ai envoyé le signal de réveil à la télé, Monsieur."

async def tv_eteindre():
    if await adb_command("input keyevent 26"): return "J'ai éteint la télé, mylane."
    return "Échec de l'extinction."

async def tv_quitter_app():
    if await adb_command("input keyevent 3"): return "J'ai fermé l'application sur la télé, mylane."
    return "Échec du retour à l'accueil."

async def tv_volume(direction, steps=5):
    """Gère le volume via ADB par paquets."""
    key = "24" if direction == "monter" else "25"
    try:
        signer = get_adb_signer()
        device = AdbDeviceTcp(TV_IP, 5555, default_transport_timeout_s=10)
        device.connect(rsa_keys=[signer], auth_timeout_s=5)
        remaining = steps
        while remaining > 0:
            batch = min(remaining, 20)
            touches = " ".join([key] * batch)
            device.shell(f"input keyevent {touches}")
            remaining -= batch
            if remaining > 0: await asyncio.sleep(0.1)
        device.close()
        return f"Volume de la télé ajusté de {steps} points, Monsieur."
    except:
        return "Le volume de la télé a été modifié."

async def tv_lancer_app(app_name):
    apps = {
        "netflix": "com.netflix.ninja", "disney": "com.disney.disneyplus",
        "prime video": "com.amazon.amazonvideo.livingroom", "youtube": "com.google.android.youtube.tv",
        "deezer": "deezer.android.tv", "twitch": "tv.twitch.android.app",
        "apple tv": "com.apple.atve.androidtv.appletv", "crunchyroll": "com.crunchyroll.crunchyroid"
    }
    pkg = apps.get(app_name.lower())
    if not pkg: return f"Je ne connais pas l'application {app_name}."
    cmd = f"monkey -p {pkg} 1"
    if app_name.lower() in ["prime video", "prime"]: cmd = f"am start -n {pkg}/com.amazon.ignition.IgnitionActivity"
    if await adb_command(cmd): return f"J'ai lancé {app_name} sur la télé, mylane."
    return f"Impossible de lancer {app_name}."

async def tv_lancer_youtube(video_id):
    cmd = f'am start -a android.intent.action.VIEW "vnd.youtube://www.youtube.com/watch?v={video_id}"'
    if await adb_command(cmd): return "C'est lancé sur votre télé, mylane !"
    return "Erreur lors du lancement YouTube."

def chercher_youtube(recherche):
    try:
        query = requests.utils.quote(recherche)
        url = f"https://www.youtube.com/results?search_query={query}"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        video_ids = re.findall(r"watch\?v=(\S{11})", resp.text)
        return video_ids[0] if video_ids else None
    except: return None

# --- RÉSOLVEUR ---

async def resoudre_tv_localement(texte):
    """Analyse les ordres relatifs à la télévision."""
    t = texte.lower().strip()
    
    if any(k in t for k in ["télé", "tv", "philips", "télévision"]):
        # Volume précis
        if any(k in t for k in ["son", "volume"]):
            direction = "monter" if any(k in t for k in ["monte", "augmente", "plus", "hausse"]) else "baisser"
            steps = 10
            if "un peu" in t: steps = 3
            if any(k in t for k in ["beaucoup", "fortement", "bien"]): steps = 25
            chiffres = re.findall(r'\d+', t)
            if chiffres: steps = int(chiffres[0])
            return await tv_volume(direction, steps)

        # Allumage / Extinction
        if any(k in t for k in ["allume", "démarre", "lance"]):
            if len(t.split()) < 5: return await tv_allumer()
        if any(k in t for k in ["éteins", "veille", "arrête"]):
            return await tv_eteindre()

        # Quitter / Accueil
        if any(k in t for k in ["ferme", "quitte", "quitter", "fermer", "accueil", "home"]):
            return await tv_quitter_app()

        # YouTube spécifique
        if "youtube" in t and any(k in t for k in ["lance", "mets", "joue"]):
            recherche = t
            for p in ["sur ma télé", "sur la télé", "sur ma tv", "sur la tv", "youtube", "mets", "joue", "lance", "ouvre", "sur la", "sur ma", "sur"]:
                recherche = recherche.replace(p, "")
            recherche = recherche.strip()
            if recherche:
                v_id = chercher_youtube(recherche)
                if v_id: return await tv_lancer_youtube(v_id)
            return await tv_lancer_app("youtube")

        # Autres Apps
        for app in ["netflix", "disney", "prime video", "deezer", "crunchyroll", "apple tv"]:
            if app in t and any(k in t for k in ["lance", "mets", "ouvre"]):
                return await tv_lancer_app(app)

        # Contrôles basiques
        if "pause" in t: await adb_command("input keyevent 85"); return "C'est fait."
        if "stop" in t: return await tv_quitter_app()

    return None

# Injection builtins
builtins.resoudre_tv_localement = resoudre_tv_localement
