import asyncio
import threading
import queue
import time
import os
import math
import random
import base64
import json
import edge_tts
import builtins

try:
    import pygame
except ImportError:
    pygame = None

# Sortie HomePod optionnelle (USE_HOMEPOD_AUDIO=true dans .env)
_USE_HOMEPOD = os.getenv("USE_HOMEPOD_AUDIO", "false").lower() == "true"
if _USE_HOMEPOD:
    try:
        from module.homepod_audio import jouer_sur_homepod
        print("[SPEECH] Mode HomePod activé — sortie audio via AirPlay.")
    except ImportError:
        _USE_HOMEPOD = False
        print("[SPEECH] homepod_audio introuvable — fallback sur pygame.")

# TTS local F5-TTS optionnel (USE_LOCAL_TTS=true dans .env)
_USE_LOCAL_TTS = os.getenv("USE_LOCAL_TTS", "false").lower() == "true"
if _USE_LOCAL_TTS:
    try:
        from core.tts_local import init_tts, generer_audio as _generer_audio_local
        init_tts()  # Charge le modèle en VRAM au démarrage
        print("[SPEECH] Mode TTS local (F5-TTS) activé.")
    except Exception as e:
        _USE_LOCAL_TTS = False
        print(f"[SPEECH] F5-TTS indisponible ({e}) — fallback edge_tts.")

is_speaking = False
speak_volume = 0.0
STOP_PARLER = False
parole_queue = queue.Queue()
parole_stop_event = threading.Event()
dernier_parle_time = 0

def init_mixer():
    if pygame and not pygame.mixer.get_init():
        pygame.mixer.init()

lecture_queue = queue.Queue()

async def _generer_tts_fichier(texte) -> str | None:
    """Génère le fichier TTS en arrière-plan et renvoie le chemin temporaire."""
    if not texte or not texte.strip():
        return None
        
    texte_tts = texte.replace("**", "").replace("*", "").replace("#", "").replace("`", "").strip()
    tmp = f"jarvis_tts_{int(time.time()*1000)}"
    
    try:
        from core.config import VOIX_ACTUELLE
        
        if _USE_LOCAL_TTS:
            # Génération locale F5-TTS (WAV) avec clone de voix
            tmp_path = tmp + ".wav"
            ok = await asyncio.get_event_loop().run_in_executor(
                None, _generer_audio_local, texte_tts, tmp_path
            )
            if not ok:
                # Fallback edge_tts si F5-TTS échoue
                tmp_path = tmp + ".mp3"
                voice_standard = "fr-FR-HenriNeural" if VOIX_ACTUELLE == "homme" else "fr-FR-DeniseNeural"
                communicate = edge_tts.Communicate(texte_tts, voice=voice_standard, rate="+20%")
                await communicate.save(tmp_path)
        else:
            tmp_path = tmp + ".mp3"
            voice_standard = "fr-FR-HenriNeural" if VOIX_ACTUELLE == "homme" else "fr-FR-DeniseNeural"
            communicate = edge_tts.Communicate(texte_tts, voice=voice_standard, rate="+20%")
            await communicate.save(tmp_path)
            
        return tmp_path
    except Exception as e:
        print(f"[SPEECH GENERATION ERROR] {e}")
        return None

async def _jouer_tts_fichier(texte, tmp_path):
    """Joue physiquement le fichier TTS pré-généré et notifie le HUD."""
    global is_speaking, speak_volume, STOP_PARLER, dernier_parle_time
    
    if STOP_PARLER:
        try:
            if os.path.exists(tmp_path): os.remove(tmp_path)
        except: pass
        return

    texte_tts = texte.replace("**", "").replace("*", "").replace("#", "").replace("`", "").strip()
    
    send_web_state = getattr(builtins, "send_web_state", None)
    send_web_text = getattr(builtins, "send_web_text", None)
    send_web_volume = getattr(builtins, "send_web_volume", None)
    connected_clients = getattr(builtins, "CONNECTED_CLIENTS", [])

    is_speaking = True
    if send_web_state: await send_web_state("speaking")
    if send_web_text: await send_web_text(texte)

    try:
        from core.config import _skip_pc_audio

        if _skip_pc_audio:
            if connected_clients:
                try:
                    with open(tmp_path, "rb") as f:
                        audio_b64 = base64.b64encode(f.read()).decode('utf-8')
                    message = json.dumps({"action": "jarvis_audio", "text": texte_tts, "audio_b64": audio_b64})
                    await asyncio.gather(*[ws.send(message) for ws in connected_clients], return_exceptions=True)
                except Exception as e:
                    print(f"[MOBILE] Erreur envoi audio : {e}")
        elif _USE_HOMEPOD:
            # Lecture sur le HomePod via AirPlay — PC reste silencieux
            speak_volume = 0.8
            if send_web_volume: await send_web_volume(speak_volume)
            ok = await jouer_sur_homepod(tmp_path, stop_checker=lambda: STOP_PARLER)
            if not ok:
                # Fallback pygame si le HomePod n'est pas joignable
                print("[SPEECH] HomePod indisponible — fallback casque.")
                if pygame:
                    init_mixer()
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        if STOP_PARLER:
                            pygame.mixer.music.stop()
                            break
                        await asyncio.sleep(0.05)
            speak_volume = 0.0
            if send_web_volume: await send_web_volume(speak_volume)
        elif pygame:
            init_mixer()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if STOP_PARLER:
                    pygame.mixer.music.stop()
                    break

                t_audio = time.time() * 20
                base_vol = 0.4 + 0.3 * math.sin(t_audio) + 0.2 * math.sin(t_audio * 0.5)
                speak_volume = max(0.1, min(1.0, base_vol + random.uniform(-0.1, 0.1)))

                if send_web_volume: await send_web_volume(speak_volume)
                await asyncio.sleep(0.05)
    except Exception as e:
        print(f"[SPEECH PLAYBACK ERROR] {e}")
    finally:
        speak_volume = 0.0
        is_speaking = False
        if send_web_state: await send_web_state("idle")
        dernier_parle_time = time.time()
        try:
            if pygame and pygame.mixer.get_init():
                pygame.mixer.music.unload()
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except: pass

def gestionnaire_generateur_worker():
    """Générateur d'audio en arrière-plan : génère les fichiers TTS en avance."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while not parole_stop_event.is_set():
        try:
            phrase = parole_queue.get(timeout=1.0)
            if STOP_PARLER:
                parole_queue.task_done()
                continue
                
            tmp_path = loop.run_until_complete(_generer_tts_fichier(phrase))
            if tmp_path:
                lecture_queue.put({"text": phrase, "file": tmp_path})
            parole_queue.task_done()
        except queue.Empty:
            continue
    loop.close()

def gestionnaire_lecture_worker():
    """Lecteur audio en arrière-plan : joue les fichiers TTS de manière séquentielle."""
    global STOP_PARLER
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while not parole_stop_event.is_set():
        try:
            item = lecture_queue.get(timeout=1.0)
            if STOP_PARLER:
                try:
                    if os.path.exists(item["file"]): os.remove(item["file"])
                except: pass
                lecture_queue.task_done()
                continue
                
            loop.run_until_complete(_jouer_tts_fichier(item["text"], item["file"]))
            lecture_queue.task_done()
        except queue.Empty:
            continue
    loop.close()

def gestionnaire_parole_worker():
    """Point d'entrée du thread JARVIS : pilote le générateur et le lecteur en parallèle."""
    t_gen = threading.Thread(target=gestionnaire_generateur_worker, daemon=True)
    t_play = threading.Thread(target=gestionnaire_lecture_worker, daemon=True)
    t_gen.start()
    t_play.start()
    
    while not parole_stop_event.is_set():
        time.sleep(0.5)

def vider_files():
    """Vide et nettoie de façon sécurisée toutes les files d'attente de parole."""
    # 1. Vider les phrases textuelles en attente
    while not parole_queue.empty():
        try:
            parole_queue.get_nowait()
            parole_queue.task_done()
        except:
            break
            
    # 2. Vider les fichiers audio générés et les purger du disque
    while not lecture_queue.empty():
        try:
            item = lecture_queue.get_nowait()
            if os.path.exists(item["file"]):
                try: os.remove(item["file"])
                except: pass
            lecture_queue.task_done()
        except:
            break

def parler(texte, print_console=True):
    if not texte or not texte.strip(): return
    if print_console:
        print(f"[JARVIS] {texte}")
    parole_queue.put(texte)

builtins.parler = parler
