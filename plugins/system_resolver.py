import os
import psutil
import pyautogui
import builtins
import random
import re
import asyncio

def nettoyer_accent(texte):
    """Supprime les accents pour faciliter la comparaison."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

async def resoudre_commandes_systeme(cmd):
    """Gère les commandes matérielles du PC (Volume, Screenshot, Système)."""
    t = nettoyer_accent(cmd.lower().strip())
    
    # 1. VOLUME PC
    if "volume" in t:
        if "augmente" in t or "plus" in t:
            for _ in range(5): pyautogui.press("volumeup")
            return "Volume PC augmente, Monsieur."
        if "baisse" in t or "moins" in t:
            for _ in range(5): pyautogui.press("volumedown")
            return "Volume PC baisse, Monsieur."
        if "muet" in t or "coupe" in t:
            pyautogui.press("volumemute")
            return "Mode muet active sur le PC."

    # 2. SCREENSHOT
    if "screenshot" in t or "capture" in t:
        try:
            import winshell
            desktop = winshell.desktop()
        except:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop): desktop = os.path.join(os.path.expanduser("~"), "Bureau")
        
        if not os.path.exists(desktop): desktop = os.getcwd()
        path = os.path.join(desktop, f"screenshot_{random.randint(1000,9999)}.png")
        pyautogui.screenshot(path)
        return f"Capture d'écran sauvegardée sur votre bureau, Monsieur."

    return None

async def resoudre_infos_systeme_localement(cmd):
    """Donne des informations sur l'état du PC."""
    t = nettoyer_accent(cmd.lower().strip())
    
    if "processeur" in t or any(w == "cpu" for w in re.findall(r'\b\w+\b', t)):
        usage = psutil.cpu_percent(interval=1)
        return f"La charge actuelle du processeur est de {usage}%, Monsieur."
        
    if "memoire" in t or any(w == "ram" for w in re.findall(r'\b\w+\b', t)):
        ram = psutil.virtual_memory()
        return f"L'utilisation de la mémoire vive est de {ram.percent}%, Monsieur."
        
    if "batterie" in t:
        batt = psutil.sensors_battery()
        if batt:
            offset_m = "en charge" if batt.power_plugged else "sur batterie"
            return f"La batterie est à {batt.percent}% et l'appareil est {offset_m}."
        return "Je ne parviens pas à détecter de batterie sur ce système, Monsieur."

    return None

# Injection builtins
builtins.resoudre_commandes_systeme = resoudre_commandes_systeme
builtins.resoudre_infos_systeme_localement = resoudre_infos_systeme_localement
