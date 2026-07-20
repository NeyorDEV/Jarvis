import time
import requests

def executer(texte_utilisateur=None):
    ip_publique = "Inconnue"
    latence = None
    status_internet = False

    # 1. Récupération de l'adresse IP publique
    try:
        response_ip = requests.get("https://api.ipify.org?format=json", timeout=5)
        if response_ip.status_code == 200:
            ip_publique = response_ip.json().get("ip", "Inconnue")
            status_internet = True
    except Exception:
        ip_publique = "Impossible de récupérer l'adresse IP"

    # 2. Mesure de la latence avec Google
    try:
        debut = time.time()
        response_ping = requests.get("https://www.google.com", timeout=5)
        fin = time.time()
        if response_ping.status_code == 200:
            latence = round((fin - debut) * 1000)  # Conversion en millisecondes
            status_internet = True
    except Exception:
        latence = None

    # 3. Construction de la réponse vocale pour JARVIS
    if not status_internet:
        return "Monsieur, il semble que vous ne soyez pas connecté à Internet actuellement. Veuillez vérifier votre connexion."

    reponse = f"Connexion établie, Monsieur. Votre adresse IP publique actuelle est le {ip_publique}."
    if latence is not None:
        reponse += f" La latence mesurée avec les serveurs de Google est de {latence} millisecondes."
    else:
        reponse += " Cependant, je n'ai pas pu mesurer précisément la latence avec Google."

    return reponse