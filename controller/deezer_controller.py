try:
    import pyautogui
except ImportError:
    pyautogui = None
import time
import pyperclip
import asyncio
import subprocess
import os
import requests

# DEEZER — méthode native Windows (win32gui + pyautogui)
# ==========================================

def _focus_deezer():
    """Met la fenêtre Deezer au premier plan. Retourne True si trouvé."""
    try:
        import win32gui, win32con
        candidats = []
        def _cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                titre = win32gui.GetWindowText(hwnd)
                if "Deezer" in titre:
                    candidats.append(hwnd)
        win32gui.EnumWindows(_cb, None)
        if not candidats:
            return False
        hwnd = candidats[0]
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.4)
        return True
    except Exception:
        return False

async def deezer_ouvrir():
    """Lance Deezer s'il n'est pas déjà ouvert via le protocole Windows natif."""
    try:
        if _focus_deezer():
            return "Deezer est déjà ouvert, mylane, je l'ai mis au premier plan."
        subprocess.Popen(["explorer", "deezer:"], shell=False)
        time.sleep(4)
        _focus_deezer()
        return "Deezer lancé, mylane."
    except Exception as e:
        return f"Je n'ai pas réussi à ouvrir Deezer : {e}"

async def deezer_lecture_pause():
    """Basculer lecture / pause via la touche média globale."""
    if pyautogui:
        pyautogui.press('playpause')
    return "Lecture/Pause, mylane."

async def deezer_suivant():
    """Piste suivante via la touche média globale."""
    if pyautogui:
        pyautogui.press('nexttrack')
    return "Piste suivante sur Deezer, mylane."

async def deezer_precedent():
    """Piste précédente via la touche média globale."""
    if pyautogui:
        pyautogui.press('prevtrack')
    return "Piste précédente sur Deezer, mylane."

async def deezer_stop():
    """Met en pause."""
    _focus_deezer()
    time.sleep(0.2)
    if pyautogui:
        pyautogui.press('playpause')
    return "Musique mise en pause sur Deezer, mylane."

async def deezer_volume(direction, paliers=4):
    """Monte ou baisse le volume général du PC."""
    if not pyautogui:
        return "Volume impossible, pyautogui non disponible."
    time.sleep(0.2)
    for _ in range(int(paliers)):
        if direction in ("monter", "up", "augmenter", "plus"):
            pyautogui.press('volumeup')
        else:
            pyautogui.press('volumedown')
        time.sleep(0.05)
    msg = "Volume monté" if direction in ("monter", "up", "augmenter", "plus") else "Volume baissé"
    return f"{msg}, mylane."

async def deezer_rechercher(recherche):
    """Recherche via l'API Deezer publique, ouvre le morceau via protocole natif Windows."""
    try:
        url = f"https://api.deezer.com/search?q={requests.utils.quote(recherche)}"
        resp = await asyncio.to_thread(requests.get, url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tracks = data.get("data", [])
            if tracks:
                track = tracks[0]
                track_id = track.get("id")
                titre = track.get("title", recherche)
                artiste = track.get("artist", {}).get("name", "")

                # Ouvrir via le protocole natif Deezer Windows
                deezer_uri = f"deezer://track/{track_id}"
                subprocess.Popen(["explorer", deezer_uri], shell=False)
                time.sleep(4)
                _focus_deezer()
                time.sleep(0.5)
                # Appuyer sur Play au cas où ce n'est pas lancé automatiquement
                if pyautogui:
                    pyautogui.press('playpause')

                return f"C'est parti mylane, je lance « {titre} » de {artiste} sur Deezer."
        return f"Je n'ai pas trouvé '{recherche}' sur Deezer, mylane."
    except Exception as e:
        return f"Erreur lors de la recherche Deezer : {e}"

async def deezer_lancer_playlist(url=None):
    """Lance la playlist Deezer via le protocole natif Windows (deezer://playlist/ID)."""
    try:
        playlist_url = url or os.getenv("DEEZER_PLAYLIST_URL")

        if playlist_url:
            # Résolution des liens courts (link.deezer.com)
            if "link.deezer.com" in playlist_url:
                try:
                    r = await asyncio.to_thread(
                        requests.head, playlist_url, allow_redirects=True, timeout=5
                    )
                    playlist_url = r.url
                except:
                    pass

            # Construire l'URI native Deezer Windows
            if "/playlist/" in playlist_url:
                p_id = playlist_url.split("/playlist/")[-1].split("?")[0]
                deezer_uri = f"deezer://playlist/{p_id}"
            else:
                deezer_uri = playlist_url

            print(f"[DEEZER] Lancement URI : {deezer_uri}")
            subprocess.Popen(["explorer", deezer_uri], shell=False)
            time.sleep(5)
            _focus_deezer()
            time.sleep(0.5)
            # Forcer la lecture si Deezer ne démarre pas automatiquement
            if pyautogui:
                pyautogui.press('playpause')
            return True

        else:
            # Pas d'URL configurée : ouvrir Deezer et mettre play
            await deezer_ouvrir()
            time.sleep(2)
            _focus_deezer()
            time.sleep(0.5)
            if pyautogui:
                pyautogui.press('playpause')
            return True

    except Exception as e:
        print(f"[DEEZER] Erreur lancement playlist : {e}")
        return False
