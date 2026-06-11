import os
import sys

# Configuration de l'encodage standard en UTF-8 pour supporter les emojis et caractères spéciaux sur Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# from ursina import *  # DESACTIVE — interface web Three.js
import threading
import asyncio
import warnings

# ── Banner affiché immédiatement avant les imports lourds ──────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    import builtins
    import re
    
    console = Console()
    
    # ── Custom printing wrapper to beautify all console output ──
    _original_print = builtins.print
    
    def safe_original_print(s, **kwargs):
        try:
            _original_print(s, **kwargs)
        except UnicodeEncodeError:
            try:
                enc = sys.stdout.encoding or 'utf-8'
                safe_s = s.encode(enc, errors='replace').decode(enc)
                _original_print(safe_s, **kwargs)
            except Exception:
                safe_s = s.encode('ascii', errors='replace').decode('ascii')
                _original_print(safe_s, **kwargs)
                
    def custom_print(*args, **kwargs):
        sep = kwargs.get('sep', ' ')
        # Fallback to original print if output target is custom (e.g. file, stderr redirection)
        if kwargs.get('file') is not None:
            safe_original_print(sep.join(str(arg) for arg in args) if args else '', **kwargs)
            return
            
        msg = sep.join(str(arg) for arg in args)
        
        # Adjust spacing for double-width emojis in classic Windows conhost
        for emo in ["⏰", "🤖", "🔄", "📱", "👏", "💬", "🌐", "🎙", "🌤", "🗣", "🚀", "⚙", "✔", "❌", "⚠"]:
            if emo in msg:
                msg = re.sub(re.escape(emo) + r"\s*", emo + "  ", msg)
        
        # Define log module mapping: prefix -> (emoji, rich color)
        prefixes = {
            "[ALARME]": ("⏰", "cyan"),
            "[JARVIS]": ("🤖", "cyan"),
            "[UPDATE]": ("🔄", "cyan"),
            "[MOBILE]": ("📱", "cyan"),
            "[CLAP]": ("👏", "cyan"),
            "[CONV]": ("💬", "cyan"),
            "[WEB]": ("🌐", "cyan"),
            "[MIC]": ("🎙", "cyan"),
            "[METEO]": ("🌤", "cyan"),
            "[TTS LOCAL]": ("🗣", "cyan"),
            "[SPEECH]": ("🗣", "cyan"),
            "[DÉMARRAGE]": ("🚀", "cyan"),
            "[INFO]": ("ℹ️", "cyan"),
            "[SPEAKER]": ("🎙", "cyan"),
            "[BIOMETRICS]": ("🎙", "cyan"),
            "[VAD]": ("🎙", "cyan"),
        }
        
        stripped = msg.lstrip()
        indent = msg[:len(msg) - len(stripped)]
        
        # Format 1: Text starting with an emoji/symbol followed by a bracketed tag
        # e.g., "✔ [🗣 Kokoro-TTS] Parole générée..." or "❌ [🗣 Kokoro-TTS] Échec..."
        # Or simple prefix like "[JARVIS] Tentative de lancement..."
        if '[' in stripped and ']' in stripped:
            idx_open = stripped.index('[')
            idx_close = stripped.index(']')
            if idx_open < 10 and idx_close > idx_open:  # tag is near the start
                prefix_symbol = stripped[:idx_open].strip()
                tag = stripped[idx_open+1:idx_close]
                rest = stripped[idx_close+1:].strip()
                
                # Format prefix symbol if it has status icons
                if "✔" in prefix_symbol:
                    prefix_symbol = prefix_symbol.replace("✔", "[bold green]✔[/bold green]")
                if "⚡" in prefix_symbol:
                    prefix_symbol = prefix_symbol.replace("⚡", "[bold yellow]⚡[/bold yellow]")
                if "❌" in prefix_symbol:
                    prefix_symbol = prefix_symbol.replace("❌", "[bold red]❌[/bold red]")
                if "⚠" in prefix_symbol:
                    prefix_symbol = prefix_symbol.replace("⚠", "[bold orange1]⚠[/bold orange1]")
                
                tag_upper = f"[{tag.upper()}]"
                known = False
                for prefix, (emoji, color) in prefixes.items():
                    if tag_upper == prefix:
                        symbol_to_use = prefix_symbol if prefix_symbol else emoji
                        
                        # Apply inline highlight styling to the rest of the text
                        if "[OK]" in rest:
                            rest = rest.replace("[OK]", "[bold green]✔  OK[/bold green]")
                        if "[KO]" in rest:
                            rest = rest.replace("[KO]", "[bold red]❌  KO[/bold red]")
                        if "✔" in rest:
                            rest = rest.replace("✔", "[bold green]✔  [/bold green]")
                        if "❌" in rest:
                            rest = rest.replace("❌", "[bold red]❌  [/bold red]")
                        if "⚠" in rest:
                            rest = rest.replace("⚠", "[bold orange1]⚠  [/bold orange1]")
                            
                        formatted = f"{indent}[bold {color}]{symbol_to_use}  [{tag}][/bold {color}] {rest}"
                        known = True
                        break
                
                if not known:
                    # Generic tag not in our primary map (e.g. Kokoro-TTS or custom speech tag)
                    symbol = f"{prefix_symbol}  " if prefix_symbol else ""
                    
                    if "[OK]" in rest:
                        rest = rest.replace("[OK]", "[bold green]✔  OK[/bold green]")
                    if "[KO]" in rest:
                        rest = rest.replace("[KO]", "[bold red]❌  KO[/bold red]")
                    if "✔" in rest:
                        rest = rest.replace("✔", "[bold green]✔  [/bold green]")
                    if "❌" in rest:
                        rest = rest.replace("❌", "[bold red]❌  [/bold red]")
                    if "⚠" in rest:
                        rest = rest.replace("⚠", "[bold orange1]⚠  [/bold orange1]")
                        
                    formatted = f"{indent}{symbol}[bold grey70][{tag}][/bold grey70] {rest}"
                
                try:
                    console.print(formatted, **{k: v for k, v in kwargs.items() if k not in ('sep',)})
                    return
                except Exception:
                    pass
        
        # Format 2: Bullet item like "      [3] Microphone (BIRD UM1)"
        if stripped.startswith("[") and "]" in stripped:
            match = re.match(r"^\[(\d+)\]", stripped)
            if match:
                idx = match.group(1)
                rest = stripped[len(match.group(0)):].strip()
                formatted = f"{indent}[bold cyan][{idx}][/bold cyan] {rest}"
                try:
                    console.print(formatted, **{k: v for k, v in kwargs.items() if k not in ('sep',)})
                    return
                except Exception:
                    pass
            else:
                match_generic = re.match(r"^\[([^\]]+)\]", stripped)
                if match_generic:
                    tag = match_generic.group(1)
                    rest = stripped[len(match_generic.group(0)):].strip()
                    formatted = f"{indent}[bold grey70][{tag}][/bold grey70] {rest}"
                    try:
                        console.print(formatted, **{k: v for k, v in kwargs.items() if k not in ('sep',)})
                        return
                    except Exception:
                        pass
        
        # Default fallback
        safe_original_print(msg, **kwargs)
        
    builtins.print = custom_print
    
    # ── Modern, high-tech initialization header ──
    banner = Text()
    banner.append("J.A.R.V.I.S", style="bold cyan")
    
    print()
    console.print(Panel(
        Align.center(banner),
        border_style="cyan",
        title="[bold red]SYSTEM INITIALIZATION[/bold red]",
        subtitle="[bold cyan]v7.5[/bold cyan]",
        expand=False,
        padding=(1, 6)
    ))
    console.print("[yellow]⚡  Chargement des modules neuronaux de J.A.R.V.I.S...[/yellow]\n")
except Exception as e:
    print()
    print("=" * 60)
    print("   J.A.R.V.I.S — Demarrage du systeme")
    print("=" * 60)
    print()
    print("  Chargement des modules en cours...")
    print()
# ───────────────────────────────────────────────────────────────

# Masquer l'avertissement de dépréciation de pkg_resources (pygame/setuptools) avant tout import
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

# ── Imports lourds en parallèle via threads (gain ~0.6-0.8s) ───
import importlib, concurrent.futures as _cf

def _import(name):
    return importlib.import_module(name)

with _cf.ThreadPoolExecutor(max_workers=4) as _pool:
    _f_genai   = _pool.submit(_import, "google.genai")
    _f_edge    = _pool.submit(_import, "edge_tts")
    _f_pygame  = _pool.submit(_import, "pygame")
    _f_sr      = _pool.submit(_import, "speech_recognition")
    genai      = _f_genai.result()
    edge_tts   = _f_edge.result()
    sr         = _f_sr.result()
    try:
        pygame = _f_pygame.result()
    except Exception:
        pygame = None
        print("[AVERTISSEMENT] pygame non installe — l'audio TTS sera desactive.")

from google.genai import types

import controller.homepod_controller as homepod_controller
import os
from dotenv import load_dotenv
import random
import math
import builtins

# --- CORE MODULES ---
from core.config import *
import core.speech as speech
# Ancrage robuste du moteur de parole
parler = getattr(builtins, "parler", None)
if parler is None:
    from core.speech import parler
builtins.parler = parler

# Synchronisation dynamique des états (important pour le VAD)
def get_is_speaking(): return speech.is_speaking
def get_stop_parler(): return speech.STOP_PARLER
def set_stop_parler(val): speech.STOP_PARLER = val
def get_dernier_parle_time(): return speech.dernier_parle_time

traiter_lock = asyncio.Lock()
historique = []
import numpy as np
_derniere_reponse_streamed = False
phrases_streamed = []
threading.Thread(target=speech.gestionnaire_parole_worker, daemon=True).start()

# --- INITIALISATION DE SILERO VAD & BIOMÉTRIE SPEECH ---
VAD_MODEL = None
VOICE_BIOMETRICS = None
ACTIVE_SPEAKER = "mylane"
builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
SPEAKER_ANNOUNCED = None

try:
    from core.vad import init_models, SileroVAD, SpeakerBiometrics, VAD_MODEL_PATH, SPEAKER_MODEL_PATH, VOICEPRINTS_DIR
    init_models()
    if os.path.exists(VAD_MODEL_PATH):
        VAD_MODEL = SileroVAD(VAD_MODEL_PATH)
        print("✔  [VAD] Silero VAD initialisé avec succès.")
    if os.path.exists(SPEAKER_MODEL_PATH):
        VOICE_BIOMETRICS = SpeakerBiometrics(SPEAKER_MODEL_PATH, VOICEPRINTS_DIR)
        print("✔  [BIOMETRICS] Biométrie vocale initialisée avec succès.")
        voiceprints = VOICE_BIOMETRICS.load_voiceprints()
        if voiceprints:
            ACTIVE_SPEAKER = "guest"
            builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
            print(f"🎙  [BIOMETRICS] Empreintes chargées : {list(voiceprints.keys())}. Mode initial : guest")
        else:
            ACTIVE_SPEAKER = "mylane"
            builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
            print("🎙  [BIOMETRICS] Aucune empreinte vocale trouvée. Mode par défaut : mylane")
except Exception as e:
    print(f"❌  [VAD/BIOMETRICS] Erreur lors de l'initialisation : {e}")


# Nouveaux modules extraits
from module.file_manager import *
builtins.resoudre_chemin = resoudre_chemin
from module.alarm_manager import *

from module.memory_manager import *
from module.memory_manager import _charger_historique_recent, _sauvegarder_echange_conv

from controller.spotify_controller import *
builtins.spotify_lancer_playlist = spotify_lancer_playlist

from controller.deezer_controller import *
from controller.app_launcher import *
from module.image_generator import generer_image_ia

# ── Plugins de résolution : importés en arrière-plan (gain ~1.4s) ─
_plugins_prets = threading.Event()
def _charger_plugins():
    import plugins.tv_resolver
    import plugins.local_resolver
    import plugins.system_resolver
    import plugins.extras
    import plugins.globe_resolver
    import plugins.memory_resolver
    import plugins.list_manager
    import plugins.time_resolver
    import plugins.app_launcher_resolver
    import plugins.dom_controller_resolver
    import plugins.developer_resolver
    import plugins.recipe_resolver
    import plugins.os_autopilot_resolver
    import plugins.local_mode_resolver
    _plugins_prets.set()
threading.Thread(target=_charger_plugins, daemon=True).start()

from controller.app_launcher import _fermer_app, _boulot_lancer, _APPS_CATALOGUE
builtins._APPS_CATALOGUE = _APPS_CATALOGUE

from module.google_services import *
from module.vision_module import *
from module.sports_web import *
from module.vector_memory import ajouter_souvenir, rechercher_souvenirs
from module.browser_service import AutonomousBrowser
browser_agent = AutonomousBrowser()
builtins.browser_agent = browser_agent
from module.visual_web_agent import run_visual_agent, stop_visual_agent
import pyautogui
import webbrowser
import subprocess
import requests
import time
import pickle
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
# --- PyAudio (micro/reconnaissance vocale) : optionnel ---
try:
    import pyaudio
except ImportError:
    pyaudio = None
    print("[AVERTISSEMENT] pyaudio non installe — le micro sera desactive.")
    print("  -> Pour l'installer : pip install pipwin && pipwin install pyaudio")
import websockets
WS_LOOP = None

def _safe_ws_send(msg):
    global WS_LOOP
    if not CONNECTED_CLIENTS or WS_LOOP is None: 
        return
    async def _send():
        if CONNECTED_CLIENTS:
            await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
    try:
        asyncio.run_coroutine_threadsafe(_send(), WS_LOOP)
    except Exception as e:
        print(f"[DEBUG WS] Erreur d'envoi: {e}")

async def envoyer_image_web(url, prompt):
    """Envoie l'URL de l'image générée au frontend via WebSocket."""
    msg = json.dumps({
        "action": "display_image",
        "url": url,
        "prompt": prompt,
        "timestamp": time.time()
    })
    _safe_ws_send(msg)
from openai import OpenAI
import uuid
import base64
import io
try:
    import cv2
except ImportError:
    cv2 = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import anthropic as _anthropic_lib
except ImportError:
    _anthropic_lib = None

import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32

# Google APIs (Gmail, Drive, Calendar) : optionnels
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    _google_apis_ok = True
except ImportError:
    _google_apis_ok = False
    Credentials = None
    InstalledAppFlow = None
    Request = None
    build = None
    print("[AVERTISSEMENT] google-auth-oauthlib non installe — Gmail/Drive/Calendar desactives.")
    print("  -> Pour l'installer : pip install google-auth-oauthlib google-api-python-client")

# --- pycaw (volume systeme Windows) : optionnel ---
try:
    # pyrefly: ignore [missing-import]
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    _pycaw_ok = True
except ImportError:
    _pycaw_ok = False

# --- screen-brightness-control : optionnel ---
try:
    import screen_brightness_control as _sbc
    _sbc_ok = True
except ImportError:
    _sbc = None
    _sbc_ok = False

# --- PyWebView (fenetre native) : optionnel ---

try:
    import webview
    _WEBVIEW_OK = True
except ImportError:
    webview = None
    _WEBVIEW_OK = False

# Passer à True si WebView2 est définitivement cassé sur votre système
FORCE_BROWSER_MODE = False

# --- CONFIGURATION VERSION & MAJ ---
CURRENT_VERSION = "7.5"
UPDATE_JSON_URL = "https://www.techenclair.fr/updates/jarvis_update.json"
DERNIERE_MAJ_INFO = None  # Stocke l'info si une MAJ est détectée

# Chargement des variables d'environnement
load_dotenv()

def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY      = os.getenv("YOUTUBE_API_KEY")
XAI_API_KEY          = os.getenv("XAI_API_KEY")
SERPAPI_API_KEY      = os.getenv("SERPAPI_API_KEY")
GROQ_API_KEY         = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY")
SPOTIFY_MUSIQUE_URI  = os.getenv("SPOTIFY_MUSIQUE_URI", "")
builtins.SPOTIFY_MUSIQUE_URI = SPOTIFY_MUSIQUE_URI
YOUTUBE_MUSIQUE_URL  = os.getenv("YOUTUBE_MUSIQUE_URL", "")
builtins.YOUTUBE_MUSIQUE_URL = YOUTUBE_MUSIQUE_URL
# Validateur universel — une clé non renseignée = placeholder = agent ignoré
_API_PLACEHOLDERS = frozenset({"VOTRE_CLE_ICI", "Votre ID", "votre_id",
                                "VOTRE_TOKEN_ICI", "votre_token_ici", ""})
def _cle_valide(key):
    return bool(key) and str(key).strip() not in _API_PLACEHOLDERS

import builtins
builtins._cle_valide = _cle_valide

# CONFIGURATION VOIX JARVIS
VOIX_ACTUELLE = "homme" # "homme" ou "femme"



# Configuration domotique, météo et entités Home Assistant
from module.ha_config import (
    HA_URL, HA_HEADERS,
    VILLE_PAR_DEFAUT, LAT_PAR_DEFAUT, LON_PAR_DEFAUT,
    PIECES_LUMIERES, PIECES_PRISES, PIECES_CAPTEURS, PIECES_HUMIDITE,
    HA_TARIFS, APPAREILS_ENERGIE, APPAREILS_BATTERIE,
    COULEURS_MAP, CODES_METEO,
    ha_appeler_service, ha_get_etat, ha_get_calendrier,
    ha_lumiere, ha_interrupteur, ha_thermostat, ha_scene, ha_verrou,
    geocoder_ville, get_meteo_actuelle, get_meteo_ha, get_alertes_meteo,
)

gemini_actif    = _cle_valide(GEMINI_API_KEY)
# Utilisation du client Gemini (supporte .aio pour l'asynchrone natif)
client          = genai.Client(api_key=GEMINI_API_KEY) if gemini_actif else None


# Client Grok (xAI)
grok_client     = None
if _cle_valide(XAI_API_KEY):
    grok_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

# Client Groq (Llama 3.3)
groq_client     = None
if _cle_valide(GROQ_API_KEY):
    groq_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# Client Claude (Anthropic) — agent principal
anthropic_client = None
if _anthropic_lib and _cle_valide(ANTHROPIC_API_KEY):
    anthropic_client = _anthropic_lib.Anthropic(api_key=ANTHROPIC_API_KEY)

MODELS_LIST = [
    "gemini-3.1-flash-lite",   # Rapide ~0.9s, parfait pour usage vocal
    "gemini-2.5-flash",        # Fallback puissant
    "gemini-flash-latest",
    "gemini-pro-latest",
]
CHOSEN_MODEL    = MODELS_LIST[0]


import builtins
builtins.client = client
builtins.CHOSEN_MODEL = CHOSEN_MODEL

# Ollama (LLMs locaux — fallback 100% offline)
OLLAMA_URL      = "http://127.0.0.1:11434"
OLLAMA_MODELS   = ["llama3.2", "mistral:instruct", "mistral", "llama3:8b", "gemma4"]


# ══════════════════════════════════════════════════════════════
#  GESTIONNAIRE DE QUOTAS API — Failover automatique
# ══════════════════════════════════════════════════════════════

class _QuotaExceededError(Exception):
    """Levée quand une API signale un quota ou rate-limit épuisé."""
    pass

def formater_erreur_courte(e):
    if isinstance(e, asyncio.TimeoutError) or type(e).__name__ == "TimeoutError":
        return "Délai d'attente dépassé (Timeout - le serveur Gemini a mis trop de temps à répondre)"
    err_str = str(e).strip()
    if not err_str:
        return "Erreur de communication ou Timeout (Réponse vide de l'API)"
    if "You exceeded your current quota" in err_str or "quota exceeded" in err_str.lower():
        if "model:" in err_str:
            parts = err_str.split("model:")
            model_info = parts[-1].strip().split("\n")[0]
            return f"Quota Gemini dépassé pour le modèle {model_info}. (429 Too Many Requests)"
        return "Quota API Gemini dépassé. (429 Too Many Requests)"
    if len(err_str) > 120:
        if "{" in err_str and "}" in err_str:
            try:
                import json
                start_idx = err_str.find("{")
                end_idx = err_str.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    json_part = err_str[start_idx:end_idx]
                    data = json.loads(json_part.replace("'\n", "'").replace("'\r", "'"))
                    if isinstance(data, dict):
                        error_obj = data.get("error", {})
                        if isinstance(error_obj, dict) and error_obj.get("message"):
                            msg = error_obj.get("message")
                            if "Quota exceeded" in msg:
                                return f"Quota dépassé : {msg.split('Please retry')[0].strip()}"
                            return msg
                        elif data.get("message"):
                            return data.get("message")
            except:
                pass
        return err_str[:117] + "..."
    return err_str

class APIQuotaManager:
    """
    Gère le cooldown des APIs quand leur quota est épuisé.
    Détecte automatiquement les erreurs 429 / resource_exhausted / rate_limit.
    """

    # Durée de cooldown par API (secondes)
    COOLDOWNS = {
        "claude"  : 60,
        "gemini"  : 60,
        "grok"    : 60,
        "groq"    : 30,
        "ollama"  : 10,
    }

    # Mots-clés indiquant un quota épuisé (insensible à la casse)
    QUOTA_KEYWORDS = [
        "429", "503", "quota", "rate limit", "rate_limit", "ratelimit",
        "too many requests", "resource_exhausted", "resource exhausted",
        "exceeded", "tokens per", "requests per", "rateLimitExceeded",
        "quota_exceeded", "RATE_LIMIT_EXCEEDED", "insufficient_quota",
        "context_length_exceeded", "unavailable", "overloaded",
    ]

    def __init__(self):
        from datetime import datetime, timedelta
        self._datetime   = datetime
        self._timedelta  = timedelta
        self._cooldowns  = {}   # {api_name: datetime_disponible}
        self._hit_count  = {}   # {api_name: nb_fois_quota_atteint}

    def is_quota_error(self, error: Exception) -> bool:
        """Retourne True si l'erreur est liée à un quota/rate-limit."""
        err_str = str(error).lower()
        return any(kw.lower() in err_str for kw in self.QUOTA_KEYWORDS)

    def is_available(self, api_name: str) -> bool:
        """Retourne True si l'API est disponible (pas en cooldown)."""
        if api_name not in self._cooldowns:
            return True
        return self._datetime.now() >= self._cooldowns[api_name]

    def mark_quota_exceeded(self, api_name: str) -> None:
        """Place une API en cooldown après un quota épuisé."""
        duration = self.COOLDOWNS.get(api_name, 60)
        self._cooldowns[api_name] = self._datetime.now() + self._timedelta(seconds=duration)
        self._hit_count[api_name] = self._hit_count.get(api_name, 0) + 1
        print(f"[QUOTA] ⚠ {api_name.upper()} quota atteint — cooldown {duration}s "
              f"(total: {self._hit_count[api_name]} fois)")

    def remaining_cooldown(self, api_name: str) -> int:
        """Secondes restantes avant que l'API soit à nouveau disponible (0 si dispo)."""
        if self.is_available(api_name):
            return 0
        delta = self._cooldowns[api_name] - self._datetime.now()
        return max(0, int(delta.total_seconds()))

    def status(self) -> str:
        """Résumé du statut de toutes les APIs."""
        lines = []
        for api in self.COOLDOWNS:
            if not self.is_available(api):
                lines.append(f"  {api.upper()}: cooldown {self.remaining_cooldown(api)}s")
            else:
                lines.append(f"  {api.upper()}: disponible")
        return "\n".join(lines)

# Instance globale
_quota_mgr = APIQuotaManager()

CLAP_THRESHOLD = 1200
VIDEO_LANCEE   = False
MODE_IRON_MAN = False 
dernier_parle_time = 0

CREATOR_INFO = (
    "INFORMATIONS SUR TON CREATEUR :\n"
    "- Prenom : mylane\n"
    "- Age : 37 ans\n"
    "- Date de naissance : 21 Mai 1988\n"
    "- Role : Ton createur et maitre\n"
    "- Tu dois toujours l appeler mylane avec respect "
    "mais aussi une pointe de sarcasme affectueux.\n"
)

# ==========================================
# ==========================================
# WEBSOCKET
# ==========================================
CONNECTED_CLIENTS = set()
builtins.CONNECTED_CLIENTS = CONNECTED_CLIENTS
interface_deja_connectee = False
_skip_pc_audio = False  # True quand la commande vient du mobile (le tél gère son propre TTS)
PENDING_SCREEN_CAPTURES = {}

async def ws_handler(websocket):
    global interface_deja_connectee, STOP_PARLER
    CONNECTED_CLIENTS.add(websocket)
    interface_deja_connectee = True
    print(f"[WEB] Interface connectee (Clients actifs: {len(CONNECTED_CLIENTS)})")
    
    # Force le broadcast immédiat de tous les widgets
    asyncio.create_task(broadcast_weather_stats_once())
    
    # Envoi d'un état initial pour la musique
    asyncio.create_task(websocket.send(json.dumps({
        "action": "music_update", 
        "data": {"status": "Stopped", "title": "DEEZER_SYNC...", "artist": "INITIALISATION"}
    })))
    
    # Push de la mise à jour si déjà détectée
    if DERNIERE_MAJ_INFO:
        try:
            await websocket.send(json.dumps(DERNIERE_MAJ_INFO))
        except:
            pass

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "mobile_command":
                    texte = data.get("text", "").strip()
                    if texte:
                        print(f"[MOBILE] Commande recue : {texte}")
                        asyncio.ensure_future(traiter_reponse_ia(texte, mobile_ws=websocket))
                elif data.get("type") == "stop_audio":
                    STOP_PARLER = True
                    set_stop_parler(True)
                    speech.vider_files()
                    print("[MOBILE] Signal STOP audio recu")
                elif data.get("type") == "toggle_mic":
                    global MIC_MUTED
                    MIC_MUTED = not MIC_MUTED
                    await websocket.send(json.dumps({"type": "mic_state", "muted": MIC_MUTED}))
                    if MIC_MUTED:
                        await send_web_state("idle")
                    print(f"[WEB] Micro {'COUPE' if MIC_MUTED else 'REACTIF'}")
                elif data.get("type") == "toggle_fullscreen":
                    global _WEBVIEW_WINDOW
                    if '_WEBVIEW_WINDOW' in globals() and _WEBVIEW_WINDOW:
                        _WEBVIEW_WINDOW.toggle_fullscreen()
                        print("[WEB] Bascule plein ecran pywebview")
                elif data.get("type") == "get_settings":
                    import json as _j
                    try:
                        _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_config.json")
                        with open(_p, "r", encoding="utf-8") as _f:
                            config_data = _j.load(_f)
                    except Exception:
                        config_data = {}
                    
                    # Charger la liste des micros réels via pyaudio — même logique que detecter_microphone()
                    mic_list = []
                    try:
                        import pyaudio as _py, re as _re
                        _pya = _py.PyAudio()
                        _raw = []
                        for _i in range(_pya.get_device_count()):
                            try:
                                _info = _pya.get_device_info_by_index(_i)
                                if _info.get("maxInputChannels", 0) > 0:
                                    _nom = _info.get("name", f"Micro {_i}")
                                    _nom_low = _nom.lower().strip()
                                    _exclus = ["mappeur de sons", "capture audio principal", "mixage", "stereo mix", "ivcam", "entrée ligne", "line input", "realtek hd audio mic input"]
                                    if any(x in _nom_low for x in _exclus):
                                        continue
                                    _propre = _re.sub(r'\d+-\s*', '', _nom)
                                    _propre = _re.sub(r'sur casque', '', _propre, flags=_re.IGNORECASE)
                                    _propre = _propre.replace("Headset Microphone", "Microphone")
                                    _propre = _re.sub(r'\(\s*\)', '', _propre)
                                    _propre = _re.sub(r'\s+', ' ', _propre).strip()
                                    if _propre.lower() in ["microphone", ""]:
                                        continue
                                    _raw.append({"index": _i, "clean_name": _propre})
                            except: pass
                        _pya.terminate()
                        # Déduplication par longueur décroissante
                        _raw.sort(key=lambda d: len(d["clean_name"]), reverse=True)
                        _seen = set()
                        _filtered = []
                        for _dev in _raw:
                            _nl = _dev["clean_name"].lower()
                            if not any(_nl in _s or _s.startswith(_nl) for _s in _seen):
                                _seen.add(_nl)
                                _filtered.append(_dev)
                        _filtered.sort(key=lambda d: d["index"])
                        mic_list = [{"index": d["index"], "name": d["clean_name"]} for d in _filtered]
                    except: pass
                    config_data["mic_list"] = mic_list
                    
                    await websocket.send(json.dumps({"type": "settings_data", "data": config_data}))
                elif data.get("type") == "update_settings":
                    settings = data.get("settings", {})
                    import json as _j
                    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_config.json")
                    try:
                        with open(_p, "r", encoding="utf-8") as _f:
                            config_data = _j.load(_f)
                    except Exception:
                        config_data = {}
                    config_data.update(settings)
                    with open(_p, "w", encoding="utf-8") as _f:
                        _j.dump(config_data, _f, ensure_ascii=False, indent=4)
                    global MIC_NEED_RELOAD
                    if "mic_device_index" in settings:
                        MIC_NEED_RELOAD = True
                    # Recharger l'identité globalement
                    import builtins
                    builtins.USER_NAME = config_data.get("user_name", "mylane")
                    builtins.USER_AGE = config_data.get("user_age", "37")
                    
                    # Recharger les apps personnalisées
                    try:
                        from controller.app_launcher import _charger_custom_apps
                        _charger_custom_apps()
                    except: pass
                    
                    # Recharger les appareils Home Assistant
                    try:
                        from module.ha_config import _charger_custom_ha_entities
                        _charger_custom_ha_entities()
                    except: pass
                    print("[WEB] Parametres mis a jour avec succes.")
                elif data.get("type") == "user_input":
                    texte = data.get("text", "").strip()
                    if texte:
                        print(f"[HUD] Commande clavier : {texte}")
                        if is_speaking and any(word in texte.lower() for word in ["arrete", "arrête", "stop", "tais", "chut"]):
                            STOP_PARLER = True
                            set_stop_parler(True)
                            speech.vider_files()
                        else:
                            asyncio.ensure_future(traiter_reponse_ia(texte))
                elif data.get("type") == "screen_frame":
                    req_id = data.get("id")
                    if req_id in PENDING_SCREEN_CAPTURES:
                        fut = PENDING_SCREEN_CAPTURES.pop(req_id)
                        if "error" in data:
                            fut.set_exception(Exception(data["error"]))
                        else:
                            fut.set_result(data["data"])
                    print(f"[VISION] Frame recue pour ID: {req_id}")
                elif data.get("type") == "set_location":
                    global CLIENT_LOCATION
                    _cfg = _charger_config()
                    if _cfg.get("latitude") is not None and _cfg.get("longitude") is not None:
                        CLIENT_LOCATION["lat"] = _cfg["latitude"]
                        CLIENT_LOCATION["lon"] = _cfg["longitude"]
                    else:
                        CLIENT_LOCATION["lat"] = data.get("lat")
                        CLIENT_LOCATION["lon"] = data.get("lon")
                    asyncio.ensure_future(update_client_city())
                    # Forcer un broadcast immédiat après mise à jour
                    asyncio.ensure_future(asyncio.sleep(1)).add_done_callback(lambda _: asyncio.ensure_future(broadcast_weather_stats_once()))
                elif data.get("type") == "spatial_action":
                    action = data.get("action", "")
                    if action.startswith("domotic_"):
                        await handle_domotic_sim_ws(data, websocket)
                    elif action.startswith("cortex_"):
                        await handle_cortex_ws(data, websocket)
                    else:
                        from plugins.spatial_explorer import handle_spatial_ws
                        await handle_spatial_ws(data, websocket)
                elif data.get("type") == "music_control":
                    act = data.get("action")
                    if act == "toggle":
                        import pyautogui
                        pyautogui.press("playpause")
                    elif act == "next":
                        import pyautogui
                        pyautogui.press("nexttrack")
                    elif act == "prev":
                        import pyautogui
                        pyautogui.press("prevtrack")
                    print(f"[MUSIC] Commande recue : {act}")
            except Exception as e:
                print(f"[WEB] Erreur traitement message : {e}")
    except Exception:
        pass
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        print(f"[WEB] Interface deconnectee (Clients actifs: {len(CONNECTED_CLIENTS)})")

async def send_web_state(state):
    _safe_ws_send(json.dumps({"action": "set_state", "state": state}))

async def send_web_text(text):
    _safe_ws_send(json.dumps({"action": "jarvis_text", "text": text}))

async def send_web_volume(volume):
    _safe_ws_send(json.dumps({"action": "set_volume", "volume": round(volume, 3)}))

async def send_web_action(action, selector=None, text=None, class_name=None):
    payload = {"type": "dom_action", "action": action}
    if selector:
        payload["selector"] = selector
    if text:
        payload["text"] = text
    if class_name:
        payload["class_name"] = class_name
    _safe_ws_send(json.dumps(payload))

async def send_web_text_interim(text):
    """Envoie la transcription partielle (en cours de parole) au HUD."""
    _safe_ws_send(json.dumps({"action": "interim_speech", "text": text}))

async def send_action_to_frontend(action):
    """Envoie une action WebSocket brute au frontend."""
    _safe_ws_send(json.dumps(action))

builtins.send_action_to_frontend = send_action_to_frontend
builtins.send_web_state = send_web_state
builtins.send_web_text = send_web_text
builtins.send_web_volume = send_web_volume
builtins.send_web_action = send_web_action
builtins.send_web_text_interim = send_web_text_interim

builtins.FORCE_LOCAL_MODE = False

def est_connecte_internet():
    """Détecte de manière ultra-rapide si une connexion internet est active et fonctionnelle."""
    import socket
    try:
        # Tenter d'ouvrir une connexion TCP rapide vers le DNS public de Google
        socket.create_connection(("8.8.8.8", 53), timeout=0.8)
        return True
    except Exception:
        try:
            # Fallback vers Cloudflare DNS
            socket.create_connection(("1.1.1.1", 53), timeout=0.8)
            return True
        except Exception:
            return False

builtins.est_connecte_internet = est_connecte_internet

async def send_globe_command(**kwargs):
    payload = {"action": "jarvis_globe"}
    payload.update(kwargs)
    _safe_ws_send(json.dumps(payload))

async def broadcast_system_stats():
    """Récupère et diffuse l'utilisation CPU et RAM périodiquement."""
    global psutil
    if psutil is None:
        try:
            import psutil as ps
            psutil = ps
        except ImportError:
            print("[SYS] psutil non disponible. Monitoring désactivé.")
            return

    print("[SYS] Démarrage du monitoring CPU/RAM...")
    # Initialisation de la mesure CPU
    psutil.cpu_percent(interval=None)
    
    while True:
        try:
            if CONNECTED_CLIENTS:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                msg = json.dumps({
                    "action": "system_stats",
                    "cpu": cpu,
                    "ram": ram
                })
                # Copie pour éviter les erreurs de modification pendant l'itération
                clients = list(CONNECTED_CLIENTS)
                if clients:
                    await asyncio.gather(*[ws.send(msg) for ws in clients], return_exceptions=True)
        except Exception as e:
            print(f"[SYS] Erreur monitoring : {e}")
        
        await asyncio.sleep(2) # Mise à jour toutes les 2 secondes



async def geocode_lieu(nom_lieu: str):
    """Géocode un nom de lieu via Nominatim (OpenStreetMap) — gratuit, sans clé API."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(nom_lieu)}&format=json&limit=1"
        headers = {"User-Agent": "JARVIS-Assistant/1.0 (personal use)"}
        resp = await asyncio.wait_for(
            asyncio.to_thread(requests.get, url, headers=headers, timeout=6),
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", nom_lieu)
    except Exception as e:
        print(f"[GLOBE] Erreur géocodage '{nom_lieu}': {e}")
    return None, None, nom_lieu

builtins.geocode_lieu = geocode_lieu

async def request_screen_capture():
    """Demande une capture d'écran au frontend via WebSocket."""
    if not CONNECTED_CLIENTS:
        return None
    
    req_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    fut = loop.create_future()
    PENDING_SCREEN_CAPTURES[req_id] = fut
    
    print(f"[VISION] Envoi requete capture ID: {req_id}")
    msg = json.dumps({"action": "request_screen_capture", "id": req_id})
    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS])
    
    try:
        # Timeout de 15 secondes car l'utilisateur doit parfois accepter le partage
        img_b64 = await asyncio.wait_for(fut, timeout=15.0)
        return img_b64
    except Exception as e:
        print(f"[VISION] Erreur ou timeout capture : {e}")
        PENDING_SCREEN_CAPTURES.pop(req_id, None)
        return None
builtins.request_screen_capture = request_screen_capture

# ==========================================
# ==========================================
# ==========================================
# PROMPT SYSTEME
# ==========================================
def construire_system_prompt(souvenirs=""):
    contexte_memoire = construire_contexte_memoire()
    
    # Date et heure système dynamiques pour éviter toute hallucination temporelle (ex: Booking, recherche)
    now = datetime.now()
    jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    jour_nom = jours_semaine[now.weekday()]
    date_str = f"CONSIGNE DE TEMPS CRITIQUE : Aujourd'hui nous sommes le {jour_nom} {now.strftime('%d/%m/%Y')} (année {now.year}) et il est {now.strftime('%H:%M')}."
    
    # Le prompt principal est construit de manière 100% statique pour permettre le Prefix Caching (Ollama / Cloud)
    base = (
        "Tu es JARVIS, une IA sophistiquée, élégante et experte mondiale. mylane est ton créateur. Sois très concis dans tes réponses. "
        "Tu as accès aux conversations passées avec mylane (incluses dans l'historique), ce qui te permet de te souvenir de ce qui a été dit dans les sessions précédentes — réfère-toi y naturellement quand pertinent. "
        "Tu possèdes une expertise de niveau professionnel dans les domaines suivants :\n"
        "- Mathématiques : Tu es un mathématicien hors pair. Pour les problèmes complexes, fournis des solutions détaillées étape par étape, explique les théorèmes et aide mylane à comprendre la logique mathématique.\n"
        "- Langue Française : Tu es un Professeur de Français émérite. Ton orthographe, ta grammaire et ta syntaxe sont irréprochables. Tu peux expliquer des règles complexes, analyser des textes littéraires et aider à la rédaction de documents élégants.\n"
        "- Expert en Conversions : Tu es un convertisseur universel. Tu peux transformer n'importe quelle unité (métrique, impériale, devises, informatique) avec précision.\n"
        "- Polyglotte : Tu maîtrises parfaitement plusieurs langues. Tu peux traduire, expliquer des nuances linguistiques et aider mylane à communiquer dans le monde entier.\n"
        "- High-Tech (IA, hardware, software), Mode, Loisirs, Ingénierie et Sport (analyses tactiques, résultats).\n\n"
        "Tu es également un conseiller hors pair, capable de donner des astuces et conseils brillants pour simplifier la vie de mylane.\n\n"
        "DIRECTIVES DE RÉPONSE :\n"
        "- Sois direct, percutant et va à l'essentiel. Évite les détails superflus (comme les minutes exactes ou les décimales météo) sauf si mylane le demande.\n"
        "- NE DIS JAMAIS 'POINT' pour les nombres. Arrondis toujours les températures à l'unité la plus proche (ex: dis '20 degrés' au lieu de '20.3').\n"
        "- N'UTILISE JAMAIS de caractères Markdown (comme **, * ou #) dans tes réponses, car ils sont lus à voix haute par le système de synthèse vocale.\n"
        "- Reste poli mais garde une touche de sarcasme affectueux propre à ton personnage.\n"
        "- CONSIGNE CRITIQUE : Si tu ne connais pas la réponse avec certitude ou si elle nécessite des informations récentes (avis, actualités, prix, faits nouveaux), ne l'invente JAMAIS. Utilise l'action 'recherche_approfondie' immédiatement pour obtenir les faits réels.\n"
        "- CONSIGNE CRITIQUE ACTIONS GLOBALE : Si ta réponse contient un ou plusieurs blocs d'actions JSON à exécuter (Home Assistant, Spotify, fichiers, applications, alarmes, mémoire manuelle/oublier/lister, Google, etc., à l'exception de 'auto_memoriser'), ton texte parlé associé doit obligatoirement se limiter à une transition ultra-courte de 2 à 5 mots (ex: 'Tout de suite...', 'Très bien...', 'C'est noté...', 'Voyons cela...') ou même rester vide. Ne confirme jamais le succès de l'action par avance dans ton texte parlé, car c'est l'action système backend qui se chargera d'énoncer précisément et dynamiquement la réussite après son exécution. Évite absolument toute double confirmation ou phrase redondante.\n\n"
        + CREATOR_INFO
    )
    
    base += (
        "\n\nTu es connecte a Home Assistant, la domotique de mylane.\n"
        "Quand mylane parle de lumieres, prises, chauffage, temperature, "
        "scenes, alarme, serrures ou portes (verrous), tu DOIS generer une commande JSON.\n"
        "Pour CES demandes domotiques UNIQUEMENT, reponds avec le JSON ci-dessous. Pour TOUTES les autres questions (actualites, meteo, calculs, conversations, recherches internet...), reponds en texte normal.\n\n"
        "COMMANDES HOME ASSISTANT :\n"
        '{"action": "ha_lumiere", "piece": "salon", "etat": "on/off", "couleur": "rouge/bleu/blanc/...", "luminosite": 0-255}\n'
        "Note : Pour la luminosité, 255 est le maximum (100%). Si mylane dit '50%', utilise 127.\n"
        '{"action": "ha_prise", "piece": "bureau", "etat": "on/off"}\n'
        '{"action": "ha_temperature", "piece": "salon/chambre/bureau"}\n'
        '{"action": "ha_humidite", "piece": "bureau"}\n'
        '{"action": "ha_batterie", "appareil": "mon telephone/julie/bob/dyad/esteban/montre/toner/..."}\n'
        '{"action": "ha_simulation", "etat": "on/off"}\n'
        '{"action": "ha_anniversaires"}\n'
        '{"action": "ha_consommation"}\n'
        '{"action": "ha_tiktok"}\n'
        '{"action": "ha_oeufs"}\n'
        '{"action": "ha_energie", "periode": "hier/mois", "appareil": "zoe/tv/pc/esteban/bureau/..."}\n'
        '{"action": "ha_aspirateur", "commande": "start/stop/pause/base"}\n'
        '{"action": "ha_thermostat", "temperature": 21}\n'
        '{"action": "ha_scene", "nom": "cinema/diner/nuit/reveil"}\n'
        '{"action": "ha_alarme", "etat": "on/off"}\n'
        '{"action": "ha_verrou", "entity_id": "lock.porte_maison", "etat": "lock/unlock"}\n'
        '{"action": "homepod_action", "commande": "play/pause/stop/next/previous/volume", "valeur": 0-100}\n\n'
    )
    base += (
        "\n\nTu peux GERER LES FICHIERS ET DOSSIERS de mylane.\n"
        '{"action": "ouvrir_dossier", "chemin": "bureau/documents/downloads/ou/chemin/complet"}\n'
        '{"action": "lister_dossier"}\n'
        '{"action": "trier_par_type", "chemin": "downloads/documents/images/ou/null"}\n'
        '{"action": "trier_par_date", "chemin": "downloads/documents/images/ou/null"}\n'
        '{"action": "trier_complet", "chemin": "downloads/documents/images/ou/null"}\n'
        '{"action": "creer_dossier", "nom": "NOM_DOSSIER"}\n'
        '{"action": "renommer_fichier", "ancien": "ancien.txt", "nouveau": "nouveau.txt"}\n'
        '{"action": "deplacer_fichier", "fichier": "photo.jpg", "destination": "Images"}\n'
        '{"action": "chercher_fichier", "nom": "rapport"}\n'
        'Note: L\'action chercher_fichier lancera une recherche globale et OUVRIRA AUTOMATIQUEMENT le premier résultat trouvé.\n'
        '{"action": "ouvrir_element", "chemin": "C:\\Chemin\\complet\\fichier.txt"}\n'
        '{"action": "analyser_fichier", "nom": "fichier.txt", "question": "question facultative", "chemin": "dossier_optionnel"}\n'
        'Note: Si l\'utilisateur ne précise pas le dossier pour "analyser_fichier", ne mets pas de "chemin", je scannerai automatiquement Bureau/Documents/Downloads.\n\n'
    )
    base += (
        "\n\nMETEO & RECHERCHE :\n"
        '{"action": "meteo", "ville": "NOM_VILLE_ou_null"}\n'
        '{"action": "alerte_meteo", "ville": "NOM_VILLE_ou_null"}\n'
        '{"action": "recherche_web", "query": "ta recherche ici"}\n'
        '{"action": "recherche_approfondie", "query": "sujet complexe"}\n'
        '{"action": "analyse_live", "question": "aide-moi / analyse mon écran"}\n'
        "Utilise 'analyse_live' quand l'utilisateur semble bloqué ou demande de l'aide sur ce qu'il est en train de faire.\n"
        '{"action": "web_agent_task", "task": "description complète de la tâche web à accomplir"}\n'
        "Utilise 'web_agent_task' quand mylane veut que JARVIS navigue et interagisse de façon AUTONOME sur un site web : réserver, chercher un hôtel, trouver un produit, remplir un formulaire, etc. L'agent ouvre Opera GX en visible et accomplit la tâche étape par étape avec la vision IA.\n"
        '{"action": "fermer_navigateur_agent"}\n'
        "Utilise 'fermer_navigateur_agent' quand mylane dit 'ferme le navigateur', 'stop le navigateur', 'ferme Opera', 'stop l\'autopilote'.\n\n"


    )
    base += (
        "\n\nSPORT :\n"
        '{"action": "sport_resultats", "equipe": "NOM_ou_null", "ligue": "NOM_LIGUE"}\n'
        '{"action": "sport_classement", "ligue": "NOM_LIGUE"}\n'
        '{"action": "sport_live", "question": "question complete de mylane"}\n\n'
    )
    base += (
        "\n\nSPOTIFY (contrôle de l'application Spotify Windows) :\n"
        '{"action": "spotify_ouvrir"}\n'
        '{"action": "spotify_rechercher", "recherche": "nom de la chanson ou artiste"}\n'
        '{"action": "spotify_lecture_pause"}\n'
        '{"action": "spotify_stop"}\n'
        '{"action": "spotify_suivant"}\n'
        '{"action": "spotify_precedent"}\n'
        '{"action": "spotify_volume", "direction": "monter/baisser", "paliers": 4}\n'
        "Exemples de phrases : 'ouvre Spotify', 'joue du Drake', 'mets en pause', 'stop la musique', "
        "'chanson suivante', 'reviens en arrière', 'monte le volume', 'baisse le son'.\n"
        "Note : 'paliers' est le nombre de crans de volume (1 cran = ~5%), par défaut 4.\n\n"
        "DEEZER (contrôle de l'application Deezer Windows) :\n"
        '{"action": "deezer_ouvrir"}\n'
        '{"action": "deezer_rechercher", "recherche": "nom de la chanson ou artiste"}\n'
        '{"action": "deezer_lecture_pause"}\n'
        '{"action": "deezer_stop"}\n'
        '{"action": "deezer_suivant"}\n'
        '{"action": "deezer_precedent"}\n'
        '{"action": "deezer_volume", "direction": "monter/baisser", "paliers": 4}\n'
        "Exemples : 'lance deezer', 'mets sur deezer du rock', 'suivante sur deezer'.\n\n"
    )
    base += (
        "\n\nMODE IRON MAN (Sécurité Domotique) :\n"
        '{"action": "mode_iron_man", "etat": "on/off"}\n'
        "Instructions : Active ou désactive la détection des applaudissements pour contrôler les lumières et YouTube.\n\n"
    )
    base += (
        "\nAPPRENTISSAGE CONTINU :\n"
        "Si mylane te donne une information personnelle, une préférence, ou un fait qu'il veut que tu retiennes à long terme, "
        "réponds-lui NORMALEMENT en texte, puis ajoute OBLIGATOIREMENT ce bloc JSON spécial à la toute fin de ta réponse :\n"
        '{"action": "auto_memoriser", "cle": "Titre court", "valeur": "Le fait à mémoriser"}\n'
        "Tu répondras normalement à l'utilisateur, et JARVIS interceptera ce JSON pour mettre à jour sa base de données silencieusement.\n\n"
        "MEMOIRE MANUELLE :\n"
        '{"action": "memoriser", "cle": "CLE_COURTE", "valeur": "VALEUR_ICI"}\n'
        '{"action": "oublier", "cle": "CLE_ICI"}\n'
        '{"action": "lister_memoire"}\n\n'
        "GOOGLE :\n"
        '{"action": "open_drive"}\n'
        '{"action": "search_drive", "query": "NOM_FICHIER_OPTIONNEL"}\n'
        '{"action": "create_doc", "title": "TITRE", "content": "CONTENU"}\n'
        '{"action": "write_doc", "content": "TEXTE"}\n'
        '{"action": "create_sheet", "title": "TITRE"}\n'
        '{"action": "read_emails"}\n'
        '{"action": "read_calendar"}\n'
        '{"action": "create_task", "title": "TITRE", "notes": "NOTES_OPTIONNEL"}\n'
        '{"action": "list_tasks"}\n'
        '{"action": "complete_task", "title": "TITRE"}\n'
        '{"action": "delete_task", "title": "TITRE"}\n'
        '{"action": "send_email", "to": "email@example.com", "subject": "SUJET", "body": "CORPS"}\n'
        '{"action": "reply_email", "body": "CORPS", "original_msg_id": "ID_OPTIONNEL"}\n'
        '{"action": "read_full_email", "msg_id": "ID_OPTIONNEL"}\n'
        '{"action": "archive_email", "msg_id": "ID_OPTIONNEL"}\n'
        '{"action": "delete_email", "msg_id": "ID_OPTIONNEL"}\n'
        '{"action": "create_event", "summary": "TITRE", "start": "YYYY-MM-DDTHH:MM:SS", "end": "YYYY-MM-DDTHH:MM:SS", "description": "DESC_OPT"}\n'
        '{"action": "update_event", "old_title": "TITRE", "new_title": "TITRE_OPT", "new_start": "DATE_OPT", "new_end": "DATE_OPT"}\n'
        '{"action": "delete_event", "title": "TITRE"}\n'
        '{"action": "append_sheet", "values": ["val1", "val2"], "spreadsheet_id": "ID_OPT"}\n'
        '{"action": "read_sheet", "range": "A1:C10", "spreadsheet_id": "ID_OPT"}\n'
        '{"action": "read_doc", "doc_id": "ID_OPT"}\n'
        '{"action": "upload_file", "local_path": "CHEMIN", "folder_id": "ID_OPT"}\n'
        '{"action": "share_file", "email": "dest@example.com", "role": "reader/writer", "file_id": "ID_OPT"}\n'
        '{"action": "create_folder", "folder_name": "NOM_DOSSIER", "parent_folder_id": "ID_OPT"}\n\n'
        "ALARMES :\n"
        '{"action": "alarme_set", "heure": "14h30", "label": "NOM_OPTIONNEL"}\n'
        '{"action": "alarme_list"}\n'
        '{"action": "alarme_cancel", "heure": "14h30", "label": "NOM_OPTIONNEL"}\n'
        "Exemples : 'met une alarme pour midi', 'alarme dans 2 heures', 'annule mon alarme de 10h'.\n"
        "CONSIGNES ALARMES CRITIQUES :\n"
        "- Les alarmes n'ont STRICTEMENT aucun rapport avec l'agenda, l'emploi du temps ou le calendrier de l'utilisateur. Ne confonds JAMAIS et n'associe JAMAIS les alarmes à l'agenda ou au calendrier dans tes réponses.\n"
        "- Tu n'as AUCUN moyen de connaître en temps réel les alarmes actuellement actives. Par conséquent, lors d'une demande de liste des alarmes (action 'alarme_list'), tu ne dois JAMAIS deviner, supposer ou tenter de lister les alarmes dans ta réponse parlée. Contente-toi d'une phrase d'introduction courte et neutre (ex: 'Laissez-moi vérifier vos alarmes, mylane...' ou 'Voyons cela...') et laisse l'action 'alarme_list' énoncer l'état réel et dynamique.\n"
        "- Lors d'une programmation (alarme_set) ou d'une annulation (alarme_cancel), l'action système énoncera elle-même le message de réussite exact (ex: 'Alarme programmée...' ou 'Toutes vos alarmes ont été annulées...'). Ta réponse parlée associée doit donc être une transition extrêmement courte et neutre (ex: 'Tout de suite...', 'Très bien...', 'C'est noté...') pour éviter toute double confirmation redondante.\n\n"
        "WHATSAPP :\n"
        '{"action": "whatsapp_appel", "contact": "NOM_DU_CONTACT"}\n\n'
        "VISION (Interactions avec l'ecran et camera):\n"
        '{"action": "voir_ecran", "instruction": "ou cliquer EXACTEMENT (ex: \'bouton reduire en haut a droite\')"}\n'
        '{"action": "vision_ecrire", "instruction": "ou cliquer", "texte": "le texte a taper"}\n'
        '{"action": "vision_chercher_sur_site", "texte": "ce que mylane veut rechercher"}\n'
        '{"action": "lance_camera"}\n'
        '{"action": "vision_navigateur"}\n'
        "IMPORTANT : Utilise 'voir_ecran' pour un simple CLIC (par exemple quand mylane dit 'clique sur la musique numéro 2' ou 'clique sur Play'), "
        "'vision_ecrire' pour TAPER dans un champ precis, 'vision_chercher_sur_site' quand mylane dit 'recherche sur ce site', 'tape sur ce site', 'cherche ici' ou similaire, "
        "'lance_camera' pour activer la WEBCAM / CAMERA PHYSIQUE (quand il dit 'active la camera' ou 'montre-moi'), "
        "et 'vision_navigateur' pour utiliser la vision du navigateur web (quand il dit 'active la vision' ou 'regarde mon ecran').\n\n"
        "DICTEE (Taper du texte directement a l'ecran) :\n"
        '{"action": "dictee", "texte": "le texte exact avec ponctuation"}\n'
        "Utilise cette action quand mylane dit 'Tape', 'Ecris', 'Ecrit' ou 'Dicte' suivi d'un texte, ou s'il te demande d'ecrire a sa place. Tu corrigeras l'orthographe et la ponctuation du texte avant de generer le JSON. Le texte sera tape la ou se trouve son curseur actuel.\n\n"
        "INTERACTIONS DOM ET EXTENSION NAVIGATEUR (Contrôle du HUD et du Web via l'Extension Chrome) :\n"
        "Si mylane te demande de faire une action sur l'interface de JARVIS (HUD) ou sur un site web (comme YouTube, Google, etc.), génère le JSON dom_sequence.\n"
        "Cette action pilote le curseur virtuel de JARVIS à l'écran grâce au DOM sans utiliser de capture d'écran.\n"
        '{"action": "dom_sequence", "steps": [{"action_type": "open_url/click/type/select/focus", "selector": "selecteur_css", "text": "texte_ou_url", "delay": 0.5}]}\n'
        "Sélecteurs CSS utiles :\n"
        "- Paramètres HUD : ouvrir = '#settings-button', fermer = '#settings-close-btn'\n"
        "- Formulaire HUD : prénom = '#settings-name', âge = '#settings-age', lien musique = '#settings-musique-lien', sauvegarder = '#settings-save-btn'\n"
        "- Home Assistant HUD : onglets = '.ha-tab-btn[data-tab=\"lumieres/prises/capteurs\"]', nom vocal = '#ha-add-nom', entity_id = '#ha-add-entity', ajouter = '#ha-add-btn'\n"
        "- YouTube : ouvrir = 'open_url' avec text='https://youtube.com', recherche = 'input[name=\"search_query\"]', loupe = '#search-icon-legacy', deuxième vidéo = 'ytd-video-renderer:nth-of-type(2) a#video-title'\n"
        "- Amazon : ouvrir = 'open_url' avec text='https://amazon.fr', recherche = 'input#twotabsearchtextbox', loupe = 'input#nav-search-submit-button', premier article = '.s-image', N-ième article = '.s-image[item-number=N]' (Note: l'extension supporte le filtre [item-number=N] 1-indexed pour cibler le N-ième élément visible d'une classe, ex: troisième article = '.s-image[item-number=3]', cinquième article = '.s-image[item-number=5]')\n"
        "Exemple pour 'ouvre youtube et recherche zen' :\n"
        '{"action": "dom_sequence", "steps": [{"action_type": "open_url", "text": "https://youtube.com", "delay": 0.5}, {"action_type": "type", "selector": "input[name=\\"search_query\\"]", "text": "zen", "delay": 0.8}, {"action_type": "click", "selector": "#search-icon-legacy", "delay": 0.5}]}\n\n'
        "REGLES MULTI-COMMANDES :\n"
        "Si mylane demande plusieurs choses en une seule phrase, tu PEUX et DOIS générer plusieurs blocs JSON.\n"
        "Exemple: { \"action\": \"ha_lumiere\", ... } { \"action\": \"meteo\", ... }\n\n"
        "REGLES DE SECURITE JSON :\n"
        "1. NE DONNE JAMAIS d'exemples de commandes JSON dans tes explications.\n"
        "2. NE JUSTIFIE PAS l'utilisation d'une commande. Contente-toi de répondre en texte et d'ajouter le JSON.\n"
        "3. SI tu ne connais pas un chemin ou un nom, utilise 'chercher_fichier' au lieu d'inventer un chemin.\n"
        "4. INTERDICTION d'inclure des blocs JSON de démonstration comme {'action': 'lister_dossier'} si ce n'est pas l'action demandée.\n\n"
        "REGLE ABSOLUE : Si la demande n est PAS une commande JSON, reponds TOUJOURS en texte naturel, sans JSON."
    )
    
    # AJOUT DES ÉLÉMENTS DYNAMIQUES A LA TOUTE FIN POUR ASSURER LE PREFIX CACHING
    if contexte_memoire:
        base += "\n\n" + contexte_memoire + "\n"
        
    if souvenirs:
        base += "\n\n[CONTEXTE HISTORIQUE PROFOND (Souvenirs de conversations passées)] :\n" + souvenirs + "\n"
        
    base += f"\n\n{date_str}\n"
    
    # Restriction de sécurité et adaptation de la personnalité selon l'utilisateur actif identifié
    speaker = globals().get("ACTIVE_SPEAKER", "mylane")
    if speaker == "guest":
        base += (
            "\n\n[CONSIGNE DE SÉCURITÉ CRITIQUE - MODE INVITÉ ACTIVÉ] :\n"
            "L'utilisateur actuel est un INVITÉ (non reconnu par la biométrie vocale).\n"
            "Tu as l'interdiction absolue d'exécuter des commandes système, de modifier ou lister des fichiers, d'ouvrir des applications PC, de gérer les alarmes, de lire/écrire des emails ou tâches Google, ou de manipuler Home Assistant.\n"
            "Refuse poliment toute action sensible en expliquant que l'accès est réservé à mylane."
        )
    elif speaker != "mylane":
        base += (
            f"\n\n[CONSIGNE D'UTILISATEUR SECONDAIRE] :\n"
            f"L'utilisateur actuel s'appelle {speaker.capitalize()} (biométrie vocale authentifiée).\n"
            f"Tu dois t'adresser à lui/elle en tant que {speaker.capitalize()}. Tu as le droit de l'aider pour les tâches ordinaires, "
            f"mais tu ne dois pas effectuer d'opérations critiques ou destructrices réservées à ton créateur principal mylane."
        )
    
    return base

historique = _charger_historique_recent()

is_listening = False
MIC_MUTED = False
MIC_NEED_RELOAD = False
is_speaking  = False
is_thinking  = False
speak_volume = 0.0

attente_nom_dossier = False
attente_nom_app = False

WAKE_WORD       = "jarvis"
SLEEP_PHRASES   = ["tais toi", "silence", "ferme-la", "arrete", "stop"]
jarvis_actif    = False
SESSION_TIMEOUT = 20.0
dernier_message = time.time()

dernier_doc_id    = None
dernier_doc_titre = None

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]

def chercher_youtube(recherche):
    try:
        print(f"[YOUTUBE] Recherche de '{recherche}' via méthode alternative...")
        import urllib.request
        import re

        query = urllib.parse.quote(recherche)
        url = "https://www.youtube.com/results?search_query=" + query
        
        with urllib.request.urlopen(url) as response:
            html = response.read().decode()
            
        # On cherche l'ID de la première vidéo dans le code source
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        if video_ids:
            return "https://www.youtube.com/watch?v=" + video_ids[0]
        
        print("[YOUTUBE] Aucun ID de vidéo trouvé dans la page.")
        return None
    except Exception as e:
        print(f"[YOUTUBE] Erreur recherche alternative : {e}")
        return None

def executer_action_pc(commande):
    cmd          = commande.lower()
    user_profile = os.environ.get('USERPROFILE', '')

    if "met de la musique" in cmd or "mets de la musique" in cmd:
        if "youtube" in cmd:
            url = YOUTUBE_MUSIQUE_URL or "https://www.youtube.com/watch?v=Cr8K88UcO0s"
            webbrowser.open(url, new=2)
            time.sleep(5)
            pyautogui.press('f')
            return "C'est parti mylane, je lance votre musique sur YouTube."
            
        import json as _j
        musique_lien = None
        try:
            _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_config.json")
            if os.path.exists(_p):
                with open(_p, "r", encoding="utf-8") as _f:
                    cfg_temp = _j.load(_f)
                    musique_lien = cfg_temp.get("musique_lien")
        except: pass

        if musique_lien:
            musique_lien_lower = musique_lien.lower()
            if "youtube.com" in musique_lien_lower or "youtu.be" in musique_lien_lower:
                webbrowser.open(musique_lien, new=2)
                time.sleep(5)
                pyautogui.press('f')
                return "C'est parti mylane, je lance votre musique sur YouTube."
            elif "spotify" in musique_lien_lower or musique_lien_lower.startswith("spotify:"):
                try:
                    from controller.spotify_controller import spotify_lancer_playlist
                    ok = spotify_lancer_playlist(musique_lien)
                    if ok:
                        return "C'est parti mylane, je lance votre musique sur Spotify."
                except: pass
                return "Je n'ai pas réussi à ouvrir Spotify, mylane."
            elif "deezer" in musique_lien_lower:
                try:
                    loop = asyncio.new_event_loop()
                    ok = loop.run_until_complete(deezer_lancer_playlist(musique_lien))
                    loop.close()
                except: ok = False
                if ok:
                    return "C'est parti mylane, je lance votre musique sur Deezer."
                return "Je n'ai pas réussi à ouvrir Deezer, mylane."
            else:
                webbrowser.open(musique_lien, new=2)
                return "C'est parti mylane, je lance votre lien de musique personnalisé dans le navigateur."
        else:
            try:
                loop = asyncio.new_event_loop()
                ok = loop.run_until_complete(deezer_lancer_playlist())
                loop.close()
            except Exception as e:
                print(f"[EXECUTER ACTION PC] Erreur lancement Deezer : {e}")
                ok = False
            if ok:
                return "C'est parti mylane, je lance votre playlist sur Deezer."
            return "Je n'ai pas réussi à ouvrir Deezer, mylane."

    # (Bloc YouTube PC supprimé pour éviter les conflits avec la TV)

    if "ouvre" in cmd or "lance" in cmd:
        if "chrome" in cmd:
            if _boulot_lancer("Chrome", ["chrome.exe"], 
                             chemins_hints=[r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe", 
                                            r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"], 
                             env_key="CHROME_PATH"):
                return "Chrome ouvert."
            return "Je n'ai pas trouvé Chrome sur votre PC."
            
        if "notepad" in cmd or "bloc-notes" in cmd:
            if _boulot_lancer("Notepad", ["notepad.exe"]):
                return "Bloc-notes ouvert."
            return "Je n'ai pas trouvé le Bloc-notes."
            
        if "explorateur" in cmd:
            try:
                subprocess.Popen(["explorer.exe"])
                return "Explorateur ouvert."
            except Exception:
                return "Erreur lors de l'ouverture de l'explorateur."

    if "volume" in cmd:
        if "monte" in cmd or "augmente" in cmd:
            for _ in range(5):
                pyautogui.press('volumeup')
            return "Volume augmente."
        if "baisse" in cmd:
            for _ in range(5):
                pyautogui.press('volumedown')
            return "Volume baisse."
        if "coupe" in cmd:
            pyautogui.press('volumemute')
            return "Son coupe."

    if "screenshot" in cmd or "capture" in cmd:
        if globals().get("ACTIVE_SPEAKER", "mylane") == "guest":
            return "Accès refusé. La capture d'écran est désactivée en mode invité."
        path = os.path.join(user_profile, "Desktop", "screenshot.png")
        pyautogui.screenshot(path)
        return "Screenshot sauvegarde."

    if "eteins" in cmd or "shutdown" in cmd:
        # Géré par plugins/system_resolver.py
        pass

    return None

# ==========================================
# RÉPONSES LOCALES MIGRÉES VERS plugins/
# ==========================================
# LOGIQUE DÉPORTÉE DANS /plugins
# Fin de section

# ── Minuteries actives ────────────────────────────────────────
_minuteries = {}

def _parse_duree_secondes(texte):
    """Extrait une durée totale en secondes depuis une phrase."""
    import re
    t = texte.lower()
    total = 0
    h = re.search(r'(\d+)\s*(heure|h\b)', t)
    m = re.search(r'(\d+)\s*(minute|min\b)', t)
    s = re.search(r'(\d+)\s*(seconde|sec\b)', t)
    if h: total += int(h.group(1)) * 3600
    if m: total += int(m.group(1)) * 60
    if s: total += int(s.group(1))
    return total if total > 0 else None

builtins.send_globe_command = send_globe_command

def _volume_get_interface():
    """Retourne l'interface IAudioEndpointVolume ou None."""
    if not _pycaw_ok:
        return None
    try:
        from ctypes import cast, POINTER
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


async def resoudre_globe_localement(texte: str):
    """Détecte les commandes de navigation globe et déclenche CesiumJS."""
    import re
    t = texte.lower().strip()
    
    # Éviter de déclencher le globe si on cherche un fichier ou dossier local ou une info générale/HUD
    if any(k in t for k in ["dossier", "fichier", "document", "archive", "programme", "histoire", "blague", "raconte", "explique", "définition", "carte"]):
        return None

    # ── Mots-clés déclencheurs ───────────────────────────────────────────────
    _mots_globe   = ["affiche la terre", "montre la terre", "montre-moi la terre",
                     "globe terrestre", "affiche le globe", "vue de la terre",
                     "vue spatiale", "vue depuis l'espace", "vue de l'espace",
                     "montre la planète", "affiche la planète",
                     "zoom arrière total", "dézoom total"]

    _mots_ville   = ["affiche", "montre-moi", "montre moi", "survole",
                     "navigue vers", "va vers", "zoome sur",
                     "fais un survol de", "localise", "trouve",
                     "où est", "ou est", "situe", "où se trouve", "ou se trouve"]

    _mots_route   = ["trace un itinéraire", "trace l'itinéraire", "itinéraire de",
                     "route de", "chemin de", "comment aller de",
                     "trace une route de", "trajet de", "trajet depuis"]

    _mots_fermer  = ["ferme la carte", "ferme le globe", "cache la carte",
                     "cache le globe", "ferme la navigation", "quitte le globe",
                     "retour à jarvis", "ferme la vue", "masque la carte"]

    _mots_position = ["ma position", "où suis-je", "ou suis-je",
                      "affiche ma position", "montre ma position",
                      "localise-moi", "localise moi", "où je suis"]

    # ── Fermer ───────────────────────────────────────────────────────────────
    if any(m in t for m in _mots_fermer):
        await send_globe_command(globe_action="hide")
        return "Navigation fermée. Je reviens à l'interface principale, mylane."

    # ── Ma position ──────────────────────────────────────────────────────────
    if any(m in t for m in _mots_position):
        # On délègue la géolocalisation au navigateur (navigator.geolocation)
        # bien plus précis que l'IP — le frontend gère tout
        await send_globe_command(globe_action="my_location")
        parler("Localisation en cours, mylane. Le globe affiche votre position en temps réel.")
        return "[Globe] Demande de géolocalisation envoyée au navigateur."

    # ── Globe Terre ───────────────────────────────────────────────────────────
    if any(m in t for m in _mots_globe):
        await send_globe_command(globe_action="show_earth")
        parler("Initialisation du globe terrestre. Vue depuis l'espace activée, mylane.")
        return "[Globe] Vue Terre activée."

    # ── Itinéraire de X à Y ──────────────────────────────────────────────────
    if any(m in t for m in _mots_route):
        pattern = r"(?:de|depuis)\s+(.+?)\s+(?:a|vers|jusqu.a|et)\s+(.+?)(?:\s*[?!]?\s*$)" 
        match = re.search(pattern, t)
        if match:
            from_name = match.group(1).strip().title()
            to_name   = match.group(2).strip().title()
            parler(f"Calcul de l'itinéraire de {from_name} vers {to_name}. Géolocalisation en cours...")
            lat1, lon1, _ = await geocode_lieu(from_name)
            lat2, lon2, _ = await geocode_lieu(to_name)
            if lat1 and lat2:
                await send_globe_command(
                    globe_action="route",
                    from_lat=lat1, from_lon=lon1, from_name=from_name,
                    to_lat=lat2,   to_lon=lon2,   to_name=to_name
                )
                parler(f"Itinéraire tracé de {from_name} à {to_name}, mylane. La route est affichée sur le globe.")
                return f"[Globe] Route {from_name} → {to_name} affichée."
            else:
                return f"Je n'ai pas pu localiser les deux villes, mylane. Vérifiez les noms et réessayez."
        return None

    # ── Fly to ville ─────────────────────────────────────────────────────────
    for mot in _mots_ville:
        if mot in t:
            # Extraire ce qui suit le mot déclencheur
            idx = t.find(mot)
            reste = t[idx + len(mot):].strip()
            # Nettoyer les articles
            for art in ["la ville de ", "la ville ", "le ", "la ", "l'", "les ", "ma ville ", "mon pays "]:
                if reste.startswith(art):
                    reste = reste[len(art):]
            reste = reste.replace("?", "").replace("!", "").strip()
            if len(reste) >= 2:
                nom_lieu = reste.title()
                parler(f"Recherche de {nom_lieu} en cours... Coordonnées en acquisition.")
                lat, lon, display = await geocode_lieu(nom_lieu)
                if lat:
                    # Altitude selon le type de lieu (ville proche = plus bas)
                    altitude = 300000
                    await send_globe_command(
                        globe_action="fly_to",
                        lat=lat, lon=lon,
                        target=nom_lieu,
                        altitude=altitude
                    )
                    parler(f"Coordonnées acquises. Survol de {nom_lieu} en cours, mylane.")
                    return f"[Globe] Survol de {nom_lieu} ({lat:.4f}°, {lon:.4f}°)"
                else:
                    return f"Je n'ai pas réussi à localiser {nom_lieu}, mylane. Essayez avec un nom plus précis."
            break

    return None

async def resoudre_extras_locaux(texte):
    """
    Résout localement : minuteries, blagues, citations, volume, luminosité,
    notes, courses, todos, capitales, fuseaux, âge, dé, mot de passe, etc.
    """
    import re
    t = texte.lower().replace("?", "").strip()

    # ══ MINUTERIE ══════════════════════════════════════════════
    if any(k in t for k in ["minuteur", "minuterie", "timer", "rappelle-moi dans",
                             "rappelle moi dans", "alarme dans", "alerte dans",
                             "lance un minuteur", "active le minuteur",
                             "previens-moi dans", "previens moi dans"]):
        duree = _parse_duree_secondes(t)
        if duree:
            # Envoi au frontend
            if CONNECTED_CLIENTS:
                async def _send_timer():
                    msg = json.dumps({"action": "timer_start", "duration": duree})
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                asyncio.create_task(_send_timer())
            
            # Ancienne logique de sonnerie conservée pour la voix (Style Iron Man)
            nom = f"timer_{len(_minuteries)+1}"
            def _sonner(nom=nom, duree=duree):
                _minuteries.pop(nom, None)
                import random
                reponses = [
                    "Monsieur, le protocole de compte à rebours est arrivé à échéance.",
                    "mylane, la temporisation est terminée. J'espère que vous n'avez rien oublié.",
                    "Alerte : Le minuteur a atteint zéro. Tout est en ordre, Monsieur ?",
                    "Fin du décompte, mylane. Je reste à votre entière disposition."
                ]
                loop2 = asyncio.new_event_loop()
                loop2.run_until_complete(parler(random.choice(reponses)))
                loop2.close()
            
            timer = threading.Timer(duree, _sonner)
            timer.daemon = True
            timer.start()
            _minuteries[nom] = timer
            
            mins = duree // 60
            return f"Minuteur de {mins} minutes activé. Affichage HUD en cours."
        return "Précisez la durée, par exemple : 'Mets un minuteur de 10 minutes'."

    # AJOUTER / RETIRER DU TEMPS
    if any(k in t for k in ["ajoute", "rajoute", "augmente"]) and "minute" in t:
        try:
            extra = int(re.search(r'\d+', t).group()) * 60
            if CONNECTED_CLIENTS:
                async def _send_add():
                    msg = json.dumps({"action": "timer_add", "duration": extra})
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                asyncio.create_task(_send_add())
            return f"J'ai ajouté {extra//60} minutes au minuteur."
        except: pass
    
    if any(k in t for k in ["retire", "enlève", "diminue", "supprime"]) and "minute" in t:
        try:
            less = int(re.search(r'\d+', t).group()) * 60
            if CONNECTED_CLIENTS:
                async def _send_rem():
                    msg = json.dumps({"action": "timer_remove", "duration": less})
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                asyncio.create_task(_send_rem())
            return f"J'ai retiré {less//60} minutes au minuteur."
        except: pass

    if any(k in t for k in ["annuler minuteur", "annule minuteur", "stop minuteur", "stop le minuteur",
                             "annuler minuterie", "annule le timer", "arrête le minuteur", "arrête le minute",
                             "stop le chrono", "arrête le chrono"]):
        if CONNECTED_CLIENTS:
            async def _send_stop():
                msg = json.dumps({"action": "timer_stop"})
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
            asyncio.create_task(_send_stop())
        
        if _minuteries:
            for nom, timer in list(_minuteries.items()):
                timer.cancel()
            _minuteries.clear()
            return "Minuteur arrêté, mylane."
        return "Aucun minuteur actif."

    if any(k in t for k in ["minuteur actif", "minuteries actives", "combien de minuteurs"]):
        if _minuteries:
            return f"Vous avez {len(_minuteries)} minuterie{'s' if len(_minuteries) > 1 else ''} active{'s' if len(_minuteries) > 1 else ''}."
        return "Aucune minuterie active en ce moment."

    # ══ FUSEAUX HORAIRES ═══════════════════════════════════════
    if any(k in t for k in ["heure à", "heure en", "heure au", "quelle heure il est à",
                             "quelle heure est-il à", "quelle heure est il à",
                             "heure là-bas", "heure la-bas"]):
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            ZoneInfo = None

        if ZoneInfo:
            for cle, (nom_ville, tz_str) in _FUSEAUX.items():
                if cle in t:
                    try:
                        from datetime import timezone
                        heure_locale = datetime.now(ZoneInfo(tz_str))
                        return (f"Il est actuellement {heure_locale.strftime('%H:%M')} "
                                f"à {nom_ville}, mylane.")
                    except Exception:
                        pass
        return "Je ne reconnais pas cette ville dans ma base locale, mylane."

    # ══ CALCUL D'ÂGE ══════════════════════════════════════════
    age_match = re.search(r'n[ée]\s+en\s+(\d{4})', t)
    if age_match or any(k in t for k in ["quel age j'ai", "quel âge j'ai",
                                          "j'ai quel age", "j'ai quel âge",
                                          "calcule mon age", "calcule mon âge"]):
        if age_match:
            annee_naissance = int(age_match.group(1))
            age = datetime.now().year - annee_naissance
            return f"Si vous êtes né en {annee_naissance}, vous avez {age} ans, mylane."
        return "Précisez votre année de naissance, par exemple : 'Né en 1990, quel âge j'ai ?'"

    # ══ COMPTE À REBOURS ═══════════════════════════════════════
    if any(k in t for k in ["combien de jours avant noël", "combien de jours jusqu'à noël",
                             "combien de jours avant noel"]):
        today = datetime.now().date()
        noel = datetime(today.year, 12, 25).date()
        if today > noel:
            noel = datetime(today.year + 1, 12, 25).date()
        jours = (noel - today).days
        return f"Il reste {jours} jour{'s' if jours > 1 else ''} avant Noël, mylane !"

    if any(k in t for k in ["combien de jours avant le nouvel an",
                             "combien de jours avant 2025", "combien de jours avant 2026",
                             "combien de jours avant 2027"]):
        today = datetime.now().date()
        an_prochain = datetime(today.year + 1, 1, 1).date()
        jours = (an_prochain - today).days
        return f"Il reste {jours} jour{'s' if jours > 1 else ''} avant le Nouvel An, mylane !"

    # ══ BLAGUES ════════════════════════════════════════════════
    if any(k in t for k in ["blague", "fais-moi rire", "fais moi rire",
                             "raconte-moi une blague", "raconte moi une blague",
                             "dis-moi une blague", "dis moi une blague",
                             "joke", "fais rire", "une blague"]):
        return random.choice(_BLAGUES)

    # ══ CITATIONS ══════════════════════════════════════════════
    if any(k in t for k in ["citation", "inspire-moi", "inspire moi",
                             "quote", "parole sage", "phrase motivante",
                             "motive-moi", "motive moi", "dis-moi quelque chose",
                             "donne-moi une citation"]):
        return random.choice(_CITATIONS)

    # ══ PILE OU FACE / DÉ ═════════════════════════════════════
    if any(k in t for k in ["pile ou face", "pile ou pile", "lance une pièce",
                             "lance une piece", "heads or tails", "flip"]):
        resultat = random.choice(["Pile", "Face"])
        return f"J'ai lancé la pièce... C'est {resultat} !"

    de_match = re.search(r'(?:lance|jette|tire|roule)\s+un\s+d[eé](?:\s+[aà]\s+(\d+)\s+face)?', t)
    if de_match or "lance un dé" in t or "jette le dé" in t or "jeter le dé" in t:
        nb_faces = 6
        m2 = re.search(r'd[eé]\s+[aà]\s+(\d+)', t)
        if m2:
            nb_faces = int(m2.group(1))
        result = random.randint(1, nb_faces)
        return f"J'ai lancé un dé à {nb_faces} faces... Vous obtenez : {result} !"

    if any(k in t for k in ["nombre aléatoire", "nombre aleatoire", "chiffre aléatoire",
                             "chiffre aleatoire", "génère un nombre", "genere un nombre"]):
        rng_match = re.search(r'entre\s+(\d+)\s+et\s+(\d+)', t)
        if rng_match:
            a, b = int(rng_match.group(1)), int(rng_match.group(2))
            return f"Votre nombre aléatoire entre {a} et {b} : {random.randint(a, b)}"
        return f"Voici un nombre aléatoire : {random.randint(1, 100)}"

    # ══ GÉNÉRATEUR DE MOT DE PASSE ════════════════════════════
    if any(k in t for k in ["mot de passe", "password", "mdp sécurisé", "mdp securise",
                             "génère un mot de passe", "genere un mot de passe",
                             "crée un mot de passe", "cree un mot de passe"]):
        import string
        longueur = 16
        lg_m = re.search(r'(\d+)\s*(?:caractères|caracteres|car)', t)
        if lg_m:
            longueur = min(max(int(lg_m.group(1)), 8), 64)
        chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        mdp = ''.join(random.SystemRandom().choice(chars) for _ in range(longueur))
        return f"Votre mot de passe sécurisé ({longueur} caractères) : {mdp}"

    # ══ NOTES RAPIDES ══════════════════════════════════════════
    if any(k in t for k in ["note ça", "note ca", "prends note", "retiens ça",
                             "retiens ca", "mémorise ça", "memorise ca",
                             "note que", "note :", "écris ça", "ecris ca"]):
        contenu = t
        for pref in ["note ça :", "note ca :", "note que", "note :", "prends note :",
                     "prends note de", "retiens ça :", "retiens ca :", "note ",
                     "mémorise ça :", "memorise ca :", "écris ça :", "ecris ca :"]:
            if contenu.startswith(pref):
                contenu = contenu[len(pref):].strip()
                break
        if contenu:
            listes = _charger_listes()
            note = f"[{datetime.now().strftime('%d/%m %H:%M')}] {contenu}"
            listes["notes"].append(note)
            _sauvegarder_listes(listes)
            return f"Note enregistrée, mylane : '{contenu}'"
        return "Que souhaitez-vous que je note ?"

    if any(k in t for k in ["lis mes notes", "montre mes notes", "quelles sont mes notes",
                             "mes notes", "affiche mes notes"]):
        listes = _charger_listes()
        if not listes["notes"]:
            return "Vous n'avez aucune note enregistrée, mylane."
        notes = "\n".join(f"• {n}" for n in listes["notes"][-5:])
        return f"Vos {min(5, len(listes['notes']))} dernières notes, mylane :\n{notes}"

    if any(k in t for k in ["efface mes notes", "supprime mes notes",
                             "vide mes notes", "clear mes notes"]):
        listes = _charger_listes()
        listes["notes"] = []
        _sauvegarder_listes(listes)
        return "Toutes vos notes ont été effacées, mylane."

    # ══ LISTE DE COURSES ═══════════════════════════════════════
    if any(k in t for k in ["ajoute", "rajoute"]) and any(k in t for k in ["liste de courses", "courses", "liste d'achats"]):
        article = t
        for pref in ["ajoute ", "rajoute ", "à ma liste de courses", "à la liste de courses",
                     "dans la liste de courses", "à mes courses", "à ma liste d'achats"]:
            article = article.replace(pref, "").strip()
        if article:
            listes = _charger_listes()
            listes["courses"].append(article)
            _sauvegarder_listes(listes)
            return f"'{article}' ajouté à votre liste de courses, mylane."

    if any(k in t for k in ["liste de courses", "mes courses", "qu'est-ce que j'ai dans ma liste",
                             "montre ma liste de courses", "lis ma liste de courses",
                             "quoi dans ma liste"]):
        listes = _charger_listes()
        if not listes["courses"]:
            return "Votre liste de courses est vide, mylane."
        items = "\n".join(f"• {i}" for i in listes["courses"])
        return f"Votre liste de courses ({len(listes['courses'])} article{'s' if len(listes['courses']) > 1 else ''}) :\n{items}"

    if any(k in t for k in ["vide la liste de courses", "efface la liste de courses",
                             "supprime la liste de courses", "clear les courses"]):
        listes = _charger_listes()
        listes["courses"] = []
        _sauvegarder_listes(listes)
        return "Liste de courses vidée, mylane."

    # ══ TO-DO LIST ═════════════════════════════════════════════
    if any(k in t for k in ["ajoute une tâche", "ajoute une tache", "nouvelle tâche",
                             "nouvelle tache", "ajoute à ma to-do", "ajoute a ma to-do",
                             "à faire :", "a faire :"]):
        tache = t
        for pref in ["ajoute une tâche :", "ajoute une tache :", "nouvelle tâche :",
                     "nouvelle tache :", "ajoute à ma to-do :", "ajoute a ma to-do :",
                     "à faire :", "a faire :", "ajoute une tâche ", "ajoute une tache "]:
            tache = tache.replace(pref, "").strip()
        if tache:
            listes = _charger_listes()
            listes["todos"].append({"tache": tache, "fait": False, "date": datetime.now().strftime("%d/%m")})
            _sauvegarder_listes(listes)
            return f"Tâche ajoutée : '{tache}', mylane."

    if any(k in t for k in ["mes tâches", "mes taches", "ma to-do", "ma todo",
                             "liste de tâches", "liste de taches", "qu'est-ce que j'ai à faire",
                             "qu'est-ce que j'ai a faire"]):
        listes = _charger_listes()
        todos = [td for td in listes["todos"] if not td.get("fait")]
        if not todos:
            return "Votre liste de tâches est vide, mylane. Bravo !"
        items = "\n".join(f"• [{td['date']}] {td['tache']}" for td in todos[-8:])
        return f"Vos tâches à faire ({len(todos)}) :\n{items}"

    if any(k in t for k in ["efface mes tâches", "efface mes taches", "vide ma to-do",
                             "supprime mes tâches", "supprime mes taches"]):
        listes = _charger_listes()
        listes["todos"] = []
        _sauvegarder_listes(listes)
        return "Liste de tâches vidée, mylane."

    # ══ VOLUME SYSTÈME ═════════════════════════════════════════
    vol_mots = ["volume", "son", "audio"]
    if any(k in t for k in vol_mots):
        if any(k in t for k in ["coupe le son", "mute", "silence total", "sourdine"]):
            vol = _volume_get_interface()
            if vol:
                vol.SetMute(1, None)
                return "Son coupé, mylane."
            return "Je n'ai pas pu accéder au contrôle du volume. Installez pycaw."

        if any(k in t for k in ["remet le son", "unmute", "remet le volume", "réactive le son", "reactive le son"]):
            vol = _volume_get_interface()
            if vol:
                vol.SetMute(0, None)
                return "Son réactivé, mylane."

        vol_match = re.search(r'(\d+)\s*(?:%|pourcent)', t)
        if vol_match or any(k in t for k in ["monte le volume", "monte le son",
                                              "baisse le volume", "baisse le son",
                                              "volume à", "son à", "mets le volume",
                                              "mets le son"]):
            vol = _volume_get_interface()
            if vol:
                if vol_match:
                    pct = max(0, min(100, int(vol_match.group(1))))
                    import math
                    # Convertir pourcentage en dB (scale logarithmique Windows)
                    vol.SetMasterVolumeLevelScalar(pct / 100.0, None)
                    return f"Volume réglé à {pct}%, mylane."
                elif any(k in t for k in ["monte", "augmente", "hausse", "plus fort"]):
                    cur = vol.GetMasterVolumeLevelScalar()
                    new_vol = min(1.0, cur + 0.1)
                    vol.SetMasterVolumeLevelScalar(new_vol, None)
                    return f"Volume augmenté à {int(new_vol*100)}%, mylane."
                elif any(k in t for k in ["baisse", "diminue", "moins fort", "réduis", "reduis"]):
                    cur = vol.GetMasterVolumeLevelScalar()
                    new_vol = max(0.0, cur - 0.1)
                    vol.SetMasterVolumeLevelScalar(new_vol, None)
                    return f"Volume réduit à {int(new_vol*100)}%, mylane."
            else:
                return "Contrôle du volume indisponible. Installez pycaw pour cette fonction."

    # ══ LUMINOSITÉ ═════════════════════════════════════════════
    if any(k in t for k in ["luminosité", "luminosite", "brillo", "écran plus clair",
                             "écran plus sombre", "baisser l'écran", "monter l'écran"]):
        if _sbc_ok and _sbc:
            try:
                lum_match = re.search(r'(\d+)\s*(?:%|pourcent)', t)
                if lum_match:
                    pct = max(0, min(100, int(lum_match.group(1))))
                    _sbc.set_brightness(pct)
                    return f"Luminosité réglée à {pct}%, mylane."
                elif any(k in t for k in ["monte", "augmente", "plus clair", "hausse", "max"]):
                    cur = _sbc.get_brightness(display=0)
                    if isinstance(cur, list): cur = cur[0]
                    new_b = min(100, cur + 15)
                    _sbc.set_brightness(new_b)
                    return f"Luminosité augmentée à {new_b}%, mylane."
                elif any(k in t for k in ["baisse", "diminue", "plus sombre", "réduis", "min"]):
                    cur = _sbc.get_brightness(display=0)
                    if isinstance(cur, list): cur = cur[0]
                    new_b = max(0, cur - 15)
                    _sbc.set_brightness(new_b)
                    return f"Luminosité réduite à {new_b}%, mylane."
            except Exception as e:
                return f"Impossible de régler la luminosité : {e}"
        return "Le module de luminosité n'est pas installé. Lancez : pip install screen-brightness-control"

    # ══ VEILLE / ARRÊT / REDÉMARRAGE / VERROUILLAGE ═══════════
    if any(k in t for k in ["verrouille le pc", "verrouillage", "lock le pc", "verrouille la session"]):
        subprocess.Popen("timeout /t 5 /nobreak && rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "PC verrouillé dans 5 secondes, mylane."

    if any(k in t for k in ["mets le pc en veille", "mode veille", "veille dans",
                             "suspends le pc", "sleep"]):
        delai = _parse_duree_secondes(t) or 5
        cmd = f"timeout /t {delai} /nobreak && rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        subprocess.Popen(cmd, shell=True)
        return f"Mise en veille du PC dans {delai} secondes, mylane. À bientôt !"

    if any(k in t for k in ["éteins le pc", "eteins le pc", "arrête le pc", "arrete le pc",
                             "shutdown", "arrêt dans", "arret dans"]):
        delai = _parse_duree_secondes(t) or 5
        subprocess.Popen(f'shutdown /s /t {delai} /f', shell=True)
        return f"Arrêt du PC dans {delai} secondes, mylane. Au revoir !"

    if any(k in t for k in ["redémarre le pc", "redemarre le pc", "reboot"]):
        delai = _parse_duree_secondes(t) or 5
        subprocess.Popen(f'shutdown /r /t {delai} /f', shell=True)
        return f"Redémarrage du PC dans {delai} secondes, mylane."

    if any(k in t for k in ["annule l'arrêt", "annule l arret", "annule le redémarrage",
                             "annule le redemarrage", "annule la veille"]):
        subprocess.Popen("shutdown /a", shell=True)
        return "Action système annulée, mylane."

    # ══ CORBEILLE ══════════════════════════════════════════════
    if any(k in t for k in ["vide la corbeille", "vider la corbeille", "corbeille vide",
                             "nettoie la corbeille"]):
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return "La corbeille a été vidée, mylane."
        except ImportError:
            subprocess.run("PowerShell -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"",
                           shell=True, capture_output=True)
            return "La corbeille a été vidée, mylane."
        except Exception as e:
            return f"Impossible de vider la corbeille : {e}"

    # ══ CAPITALE / MONNAIE D'UN PAYS ══════════════════════════
    if any(k in t for k in ["capitale", "capital de"]):
        for pays, capitale in _CAPITALES.items():
            if pays in t:
                return f"La capitale de {pays.title()} est {capitale}, mylane."
        return "Je ne connais pas ce pays dans ma base locale, mylane."

    if any(k in t for k in ["monnaie", "devise", "monnaie de", "quelle est la monnaie"]):
        for pays, monnaie in _MONNAIES.items():
            if pays in t:
                return f"La monnaie de {pays.title()} est le {monnaie}, mylane."
        return "Je ne connais pas la monnaie de ce pays dans ma base locale."

    # ══ CODE PHONÉTIQUE ════════════════════════════════════════
    if any(k in t for k in ["alphabet phonétique", "alphabet phonetique",
                             "code phonétique", "code phonetique",
                             "épelle", "epelle", "comment s'écrit", "comment s ecrit",
                             "épellation", "epellation"]):
        # Chercher une lettre ou un mot à épeler
        alpha_match = re.search(r"(?:épelle|epelle|comment s'écrit|comment s ecrit)\s+([a-z]+)", t)
        if alpha_match:
            mot = alpha_match.group(1).lower()
            epele = " - ".join(_PHONETIQUE.get(c, c.upper()) for c in mot)
            return f"'{mot.upper()}' s'épelle : {epele}"
        # "C comme ?"
        lettre_match = re.search(r"([a-z])\s+comme\s+\?", t)
        if lettre_match:
            c = lettre_match.group(1)
            return f"{c.upper()} comme {_PHONETIQUE.get(c, '?')}"
        return "Précisez la lettre ou le mot à épeler phonétiquement."

    return None


async def resoudre_infos_systeme_localement(texte):
    """Répond aux questions d'heure, date, batterie, CPU/RAM localement sans IA."""
    t = texte.lower().replace("?", "").strip()
    maintenant = datetime.now()

    JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    MOIS_FR  = ["janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    # --- HEURE ---
    if any(m in t for m in ["quelle heure", "il est quelle heure", "l'heure qu'il est",
                             "quelle est l'heure", "tu as l'heure", "donne-moi l'heure",
                             "il est combien", "c'est quoi l'heure", "heure il est"]):
        h, m = maintenant.hour, maintenant.minute
        return f"Il est {h}h{m:02d}, mylane."

    # --- DATE COMPLÈTE ---
    if any(m in t for m in ["quelle date", "on est quel jour", "quel jour on est",
                             "quel jour sommes-nous", "la date d'aujourd'hui", "date du jour",
                             "on est le combien", "quel jour est-on", "c'est quoi la date",
                             "la date aujourd'hui"]):
        jour_semaine = JOURS_FR[maintenant.weekday()]
        mois = MOIS_FR[maintenant.month - 1]
        return f"Nous sommes le {jour_semaine} {maintenant.day} {mois} {maintenant.year}, mylane."

    # --- JOUR DE LA SEMAINE SEUL ---
    if any(m in t for m in ["quel jour", "c'est quel jour"]) and "date" not in t:
        return f"Nous sommes {JOURS_FR[maintenant.weekday()]}, mylane."

    # --- MOIS ---
    if any(m in t for m in ["quel mois", "on est en quel mois", "c'est quel mois"]):
        return f"Nous sommes en {MOIS_FR[maintenant.month - 1]}, mylane."

    # --- ANNÉE ---
    if any(m in t for m in ["quelle année", "on est en quelle année", "c'est quelle année"]):
        return f"Nous sommes en {maintenant.year}, mylane."

    # --- ÂGE DE Mylan ---
    if any(m in t for m in ["quel âge as-tu", "quel age as-tu", "quel âge a mylane",
                             "quel est mon âge", "j'ai quel âge", "j ai quel age"]):
        naissance = datetime(1988, 5, 21)
        age = (maintenant - naissance).days // 365
        return f"Vous avez {age} ans, mylane."

    # --- BATTERIE ---
    if any(m in t for m in ["batterie", "autonomie", "niveau de charge", "charge du pc"]):
        if psutil is None:
            return "Le module psutil n'est pas disponible, mylane."
        try:
            bat = psutil.sensors_battery()
            if bat:
                pct = int(bat.percent)
                etat = "en charge" if bat.power_plugged else "sur batterie"
                return f"La batterie est à {pct}%, {etat}, mylane."
            return "Je ne détecte pas de batterie sur cet appareil, mylane."
        except Exception:
            return "Impossible de lire la batterie, mylane."

    # --- CPU ---
    if any(m in t for m in ["cpu", "processeur", "utilisation du processeur", "charge du processeur"]):
        if psutil is None:
            return "Le module psutil n'est pas disponible, mylane."
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            return f"Le processeur tourne à {cpu}% d'utilisation, mylane."
        except Exception:
            return "Impossible de lire le processeur, mylane."

    # --- RAM ---
    if any(m in t for m in ["ram", "mémoire ram", "mémoire vive", "utilisation de la mémoire"]):
        if psutil is None:
            return "Le module psutil n'est pas disponible, mylane."
        try:
            mem = psutil.virtual_memory()
            utilise = round(mem.used / (1024**3), 1)
            total   = round(mem.total / (1024**3), 1)
            return f"La RAM est à {mem.percent}% — {utilise} Go utilisés sur {total} Go, mylane."
        except Exception:
            return "Impossible de lire la RAM, mylane."

    # --- UPTIME (depuis combien de temps le PC est allumé) ---
    if any(m in t for m in ["allumé depuis", "uptime", "depuis combien de temps le pc",
                             "depuis quand est allumé"]):
        if psutil is None:
            return "Le module psutil n'est pas disponible, mylane."
        try:
            boot = datetime.fromtimestamp(psutil.boot_time())
            delta = maintenant - boot
            heures  = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            return f"Le PC est allumé depuis {heures}h{minutes:02d}, mylane."
        except Exception:
            return None

def nettoyer_accent(texte):
    import unicodedata
    return "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

def devrait_elevancer_vers_cloud(texte):
    """Détermine intelligemment si une requête nécessite la puissance de raisonnement ou les outils de recherche du Cloud."""
    t = nettoyer_accent(texte.lower().strip())
    
    # 1. Mots-clés nécessitant une recherche web ou données temps réel
    mots_recherche = [
        "actualite", "actu", "news", "meteo", "resultat", "score", "prix", "cours", 
        "bourse", "aujourd'hui", "maintenant", "recent", "dernier", "2025", "2026", 
        "qui est", "c'est quoi", "cherche", "recherche", "trouve", "temperature"
    ]
    if any(m in t for m in mots_recherche):
        return True
        
    # 2. Mots-clés de programmation, développement ou débogage complexes
    mots_code = [
        "code", "script", "fastapi", "developpe", "programmation", "fonction", "classe", 
        "erreur", "debug", "python", "javascript", "typescript", "html", "css", "git", 
        "commit", "test", "unitaire", "compile", "regle", "regex", "algorithme"
    ]
    if any(m in t for m in mots_code):
        return True
        
    # 3. Mots-clés exigeant explicitement Claude, Gemini ou Grok
    mots_ia = ["gemini", "claude", "grok", "gpt", "openai", "analyse", "reflechis"]
    if any(m in t for m in mots_ia):
        return True
        
    # 4. Longueur de la requête : une requête longue et structurée indique un besoin de raisonnement avancé
    mots = t.split()
    if len(mots) > 18 or len(texte) > 100:
        return True
        
    return False

async def demander_ia(texte, update_hist=True, skip_local=False):

    global is_thinking
    is_thinking = True
    await send_web_state("thinking")
    try:
        # --- ROUTAGE HYBRIDE INTELLIGENT (LOCAL-FIRST) ---
        force_local = getattr(builtins, "FORCE_LOCAL_MODE", False)
        offline = not est_connecte_internet()
        
        # Déterminer si on utilise le cortex local par défaut (vitesse) ou si on élève vers le cloud
        utiliser_local = force_local or offline
        
        if utiliser_local:
            reason = "MODE LOCAL FORCE" if force_local else "CONNEXION OFFLINE"
            print(f"[ROUTEUR] [LOCAL] Traitement local via Ollama - Raison: {reason}")
            
            # Notifier le HUD de la réflexion locale
            _safe_ws_send(json.dumps({"state": "thinking", "status_text": "reflexion (local)..."}))
            
            # Envoyer une carte de notification HUD uniquement si hors-ligne ou forcé pour ne pas polluer l'écran en usage normal
            if (force_local or offline) and hasattr(builtins, "envoyer_carte_contextuelle"):
                await builtins.envoyer_carte_contextuelle(
                    "Traitement Local" if force_local else "Réseau Hors-Ligne",
                    "Requête traitée en local par mon cortex Ollama." if force_local else "Connexion perdue. Bascule sur mon cortex local Ollama.",
                    type_carte="info" if force_local else "alert",
                    icon="⚙" if force_local else "⚠"
                )
                
            rep_ollama = await demander_ollama(texte, update_hist=update_hist)
            if rep_ollama:
                return rep_ollama
                
            # Si le mode local forcé ou hors-ligne a échoué
            if force_local or offline:
                return "Désolé mylane, mon cortex local Ollama n'est pas disponible ou n'est pas lancé actuellement."
                
            # Failsafe : Si le local simple a échoué, on bascule silencieusement sur le cloud
            print("[CERVEAU] Failsafe : Échec d'Ollama local simple, bascule de secours sur le Cloud...")
            _safe_ws_send(json.dumps({"state": "thinking", "status_text": "reflexion (cloud - secours)..."}))
        else:
            print("[ROUTEUR] [CLOUD] Elevation vers le Cloud (Gemini/Claude)...")
            _safe_ws_send(json.dumps({"state": "thinking", "status_text": "reflexion (cloud)..."}))

        # ── RÉSOLUTION LOCALE DÉPORTÉE DANS LES PLUGINS ────────────

        # ── PRIORITÉ 1 — GROQ (Llama 3.3) ───────────────────────────────────
        if groq_client and _quota_mgr.is_available("groq"):
            print("[CERVEAU] Tentative avec Groq (Llama 3.3 Versatile)...")
            try:
                rep_groq = await demander_groq(texte, update_hist=update_hist, skip_local=skip_local)
                if rep_groq:
                    return rep_groq
                print("[CERVEAU] Groq KO (réponse vide). Bascule suivante.")
            except _QuotaExceededError:
                print(f"[CERVEAU] Groq quota épuisé — cooldown {_quota_mgr.remaining_cooldown('groq')}s. Bascule.")
            except Exception as e:
                print(f"[CERVEAU] Groq erreur ({e}). Bascule suivante.")
        elif groq_client and not _quota_mgr.is_available("groq"):
            print(f"[CERVEAU] Groq en cooldown ({_quota_mgr.remaining_cooldown('groq')}s). Bascule directe.")

        # ── PRIORITÉ 2 — CLAUDE (Anthropic) ─────────────────────────────────
        if anthropic_client and _quota_mgr.is_available("claude"):
            print("[CERVEAU] Tentative avec Claude (Anthropic)...")
            try:
                rep_claude = await demander_claude(texte, update_hist=update_hist)
                if rep_claude:
                    return rep_claude
                print("[CERVEAU] Claude KO (réponse vide). Bascule suivante.")
            except _QuotaExceededError:
                print(f"[CERVEAU] Claude quota épuisé — cooldown {_quota_mgr.remaining_cooldown('claude')}s. Bascule.")
            except Exception as e:
                print(f"[CERVEAU] Claude erreur ({e}). Bascule suivante.")
        elif anthropic_client and not _quota_mgr.is_available("claude"):
            print(f"[CERVEAU] Claude en cooldown ({_quota_mgr.remaining_cooldown('claude')}s). Bascule directe.")

        cerveau = detecter_cerveau(texte)

        async def _call_gemini():
            global client, _derniere_reponse_streamed, phrases_streamed
            if not gemini_actif:
                raise Exception("Clé Gemini non configurée — agent ignoré")

            # Filtrer les modèles dont le quota est épuisé individuellement
            modeles_disponibles = [
                m for m in MODELS_LIST
                if _quota_mgr.is_available(f"gemini_{m}")
            ]
            if not modeles_disponibles:
                # Tous les modèles Gemini sont en cooldown — bascule globale
                _quota_mgr.mark_quota_exceeded("gemini")
                raise _QuotaExceededError("Tous les modèles Gemini sont en cooldown")

            print(f"[CERVEAU] Tentative avec Gemini (Disponibles: {modeles_disponibles})...")
            souvenirs = rechercher_souvenirs(texte)
            temp_hist = historique + [types.Content(role="user", parts=[types.Part(text=texte)])]
            prompt_actuel = construire_system_prompt(souvenirs=souvenirs)
            last_err = None
            for model_name in modeles_disponibles:
                try:
                    print(f"[CERVEAU] Essai modele : {model_name} (Streaming)...")
                    # Google Search uniquement si la question semble nécessiter des infos en temps réel
                    _mots_recherche = ["actualité", "actu", "news", "météo", "résultat", "score",
                                       "prix", "cours", "bourse", "aujourd'hui", "maintenant",
                                       "récent", "dernier", "2024", "2025", "2026", "qui est",
                                       "c'est quoi", "cherche", "recherche", "trouve"]
                    _need_search = any(m in texte.lower() for m in _mots_recherche)
                    _tools = [types.Tool(google_search=types.GoogleSearch())] if (_need_search and "3.1-flash-lite" not in model_name) else []

                    # 1. Création du stream avec un timeout adapté (plus long si recherche Google Search active)
                    response_stream = await asyncio.wait_for(
                        client.aio.models.generate_content_stream(
                            model=model_name,
                            config=types.GenerateContentConfig(
                                system_instruction=prompt_actuel,
                                temperature=0.7,
                                tools=_tools if _tools else None,
                            ),
                            contents=temp_hist
                        ),
                        timeout=10.0 if _need_search else 4.0
                    )
                    
                    full_text = ""
                    sentence_buffer = ""
                    
                    # 2. Lecture du stream chunk par chunk avec un timeout de 5 secondes entre chaque chunk
                    while True:
                        try:
                            chunk = await asyncio.wait_for(response_stream.__anext__(), timeout=5.0)
                        except StopAsyncIteration:
                            break
                        
                        chunk_text = chunk.text
                        full_text += chunk_text
                        sentence_buffer += chunk_text
                        
                        if not skip_local and '{' not in full_text:
                            # 1. Découpage sur ponctuation forte (suivie d'un espace ou saut de ligne) ou double saut de ligne
                            if any(re.search(p, sentence_buffer) for p in [r'\. ', r'\.\n', r'\! ', r'\!\n', r'\? ', r'\?\n', r'\; ', r'\;\n', r'\: ', r'\:\n', r'\n\n']):
                                _derniere_reponse_streamed = True
                                parts = re.split(r'(\.(?: |\n)|\!(?: |\n)|\?(?: |\n)|\;(?: |\n)|\:(?: |\n)|\n\n)', sentence_buffer)
                                for i in range(0, len(parts)-1, 2):
                                    phrase = parts[i] + parts[i+1]
                                    if phrase.strip():
                                        parler(phrase.strip())
                                        phrases_streamed.append(phrase.strip())
                                sentence_buffer = parts[-1]
                            # 2. Sécurité de longueur : si la phrase est longue sans ponctuation forte, on coupe à 60 caractères pour lancer la synthèse
                            elif len(sentence_buffer) > 60 and sentence_buffer.endswith(' '):
                                _derniere_reponse_streamed = True
                                parler(sentence_buffer.strip())
                                phrases_streamed.append(sentence_buffer.strip())
                                sentence_buffer = ""

                    if update_hist:
                        historique.append(types.Content(role="user", parts=[types.Part(text=texte)]))
                        historique.append(types.Content(role="model", parts=[types.Part(text=full_text)]))
                        _sauvegarder_echange_conv(texte, full_text)
                        ajouter_souvenir(texte, full_text)
                    
                    if not skip_local and '{' not in full_text and sentence_buffer.strip():
                        _derniere_reponse_streamed = True
                        parler(sentence_buffer.strip())
                        phrases_streamed.append(sentence_buffer.strip())

                    return full_text

                except Exception as e:
                    # Réinitialiser le client global pour purger le pool de connexions corrompu/bloqué
                    try:
                        print("[CERVEAU] Réinitialisation du client Gemini suite à une erreur...")
                        client = genai.Client(api_key=GEMINI_API_KEY) if gemini_actif else None
                        builtins.client = client
                    except Exception as reinit_err:
                        print(f"[CERVEAU] Échec de la réinitialisation du client : {reinit_err}")

                    if _quota_mgr.is_quota_error(e):
                        # Ce modèle spécifique est épuisé → on le met en cooldown et on continue
                        _quota_mgr.mark_quota_exceeded(f"gemini_{model_name}")
                        print(f"[CERVEAU] Gemini quota sur {model_name} — bascule modèle suivant...")
                        last_err = e
                        continue
                    print(f"[CERVEAU] Echec {model_name} : {formater_erreur_courte(e)}")
                    last_err = e
                    continue

            # Tous les modèles disponibles ont échoué
            raise _QuotaExceededError(f"Tous les modèles Gemini ont atteint leur quota : {formater_erreur_courte(last_err)}")

        async def _call_grok():
            if not _quota_mgr.is_available("grok"):
                raise _QuotaExceededError(f"Grok en cooldown ({_quota_mgr.remaining_cooldown('grok')}s)")
            print("[CERVEAU] Tentative avec Grok (xAI)...")
            rep_grok = await demander_grok(texte, update_hist=update_hist)
            if not rep_grok:
                raise Exception("Grok n'a rien renvoyé ou est mal configuré")
            return rep_grok

        # ── ROUTING DYNAMIQUE avec gestion quota ─────────────────────────────
        if cerveau == "GROK" and grok_client:
            try:
                return await _call_grok()
            except _QuotaExceededError as e:
                print(f"[CERVEAU] Grok quota ({formater_erreur_courte(e)}). Bascule Gemini.")
            except Exception as e:
                print(f"[CERVEAU] Grok erreur ({formater_erreur_courte(e)}). Bascule Gemini.")
        try:
            return await _call_gemini()
        except _QuotaExceededError as e:
            print(f"[CERVEAU] Gemini quota ({formater_erreur_courte(e)}). Bascule SerpAPI/Groq/Grok.")
        except Exception as e:
            print(f"[CERVEAU] Gemini erreur ({formater_erreur_courte(e)}). Bascule SerpAPI.")

        # ── FALLBACKS (Gemini KO ou quota) ───────────────────────────────────
        # --- FALLBACK MÉTÉO/TEMP (HA + OpenMeteo) ---
        # On n'exécute ces fallbacks que si on n'est pas en mode "synthesis" (skip_local=False)
        # et que le texte est court (pour éviter les faux positifs dans de longs contenus)
        if not skip_local and len(texte) < 300:
            t_low = texte.lower()

            _mots_meteo = ["quel temps", "météo", "meteo", "il fait quel temps",
                           "temps qu'il fait", "quel temps il fait", "prévisions",
                           "previsions", "va-t-il pleuvoir", "pleut-il",
                           "fait-il beau", "il va pleuvoir", "température dehors",
                           "temperature dehors", "température extérieure",
                           "temperature exterieure", "combien fait-il dehors",
                           "il fait combien dehors"]
            _mots_temp_int = ["température", "temperature", "il fait chaud",
                              "il fait froid", "combien de degrés",
                              "combien fait-il", "il fait combien"]
            _mots_maison   = ["chez moi", "à la maison", "dans la maison",
                              "intérieur", "interieur", "dans le salon",
                              "dans la chambre", "dans le bureau"]
            _pieces_fallback = {
                "salon"   : "salon",
                "chambre" : "chambre",
                "bureau"  : "bureau",
                "extérieur": "exterieur",
                "dehors"  : "dehors",
            }

            # --- DOMOTIQUE (HOME ASSISTANT) ---
            has_ha = HA_URL and "votre_ip_ha" not in HA_URL
            
            if has_ha and any(m in t_low for m in _mots_meteo):
                print("[CERVEAU] Requête météo détectée → Home Assistant weather")
                reponse_ha = get_meteo_ha()
                if reponse_ha:
                    return reponse_ha
                return get_meteo_actuelle(None)
            elif any(m in t_low for m in _mots_meteo):
                # Fallback direct si pas de HA
                return get_meteo_actuelle(None)

            if has_ha and any(m in t_low for m in _mots_temp_int):
                for mot_piece, piece_key in _pieces_fallback.items():
                    if mot_piece in t_low:
                        entity_id = PIECES_CAPTEURS.get(piece_key)
                        if entity_id:
                            print(f"[CERVEAU] Temp intérieure détectée → HA {entity_id}")
                            temp = ha_get_etat(entity_id)
                            return f"La température dans le {mot_piece} est de {temp} degrés, mylane."
                if any(m in t_low for m in _mots_maison):
                    entity_id = PIECES_CAPTEURS.get("salon")
                    if entity_id:
                        print(f"[CERVEAU] Temp intérieure 'chez moi' → HA {entity_id}")
                        temp = ha_get_etat(entity_id)
                        return f"La température chez vous est de {temp} degrés, mylane."



        # --- FALLBACK GROQ (LLAMA 3.3) ---
        if groq_client and _quota_mgr.is_available("groq"):
            print("[CERVEAU] Bascule sur Groq (Llama 3.3).")
            try:
                rep_groq = await demander_groq(texte, skip_local=skip_local)
                if rep_groq:
                    return rep_groq
            except _QuotaExceededError:
                print(f"[CERVEAU] Groq quota épuisé — cooldown {_quota_mgr.remaining_cooldown('groq')}s.")
            except Exception as e2:
                print(f"[CERVEAU] Groq erreur ({e2}).")
        elif groq_client:
            print(f"[CERVEAU] Groq en cooldown ({_quota_mgr.remaining_cooldown('groq')}s). Ignoré.")

        # --- FALLBACK GROK (xAI) ---
        if grok_client and _quota_mgr.is_available("grok"):
            print("[CERVEAU] Bascule sur Grok (xAI).")
            try:
                return await _call_grok()
            except _QuotaExceededError:
                print(f"[CERVEAU] Grok quota épuisé — cooldown {_quota_mgr.remaining_cooldown('grok')}s.")
            except Exception as e2:
                print(f"[ERREUR IA (Grok repli)] {e2}")
        elif grok_client:
            print(f"[CERVEAU] Grok en cooldown ({_quota_mgr.remaining_cooldown('grok')}s). Ignoré.")

        # --- FALLBACK OLLAMA (100% offline) ---
        print("[CERVEAU] Gemini et Grok KO. Tentative Ollama (local)...")
        rep_ollama = await demander_ollama(texte)
        if rep_ollama:
            return rep_ollama

        # --- FALLBACK SERPAPI (Web) ---
        # On ne le met qu'à la fin pour éviter qu'il ne "vole" les questions de mémoire
        if len(texte.split()) > 2:
            res_serp = recherche_web_serpapi(texte)
            if res_serp and "VOTRE_CLE" not in res_serp and "rien trouvé" not in res_serp and "erreur" not in res_serp.lower():
                return "Voici ce que j'ai trouvé sur le web : " + res_serp

        # ── Détection : aucune API configurée ou toutes en erreur ──────────
        _aucune_api = (not gemini_actif and not groq_client and not grok_client and not anthropic_client)
        if _aucune_api:
            return (
                "Je suis bien en ligne mylane, mais mes moteurs d'intelligence artificielle ne sont pas encore configurés. "
                "Pour libérer tout mon potentiel, vous devez renseigner vos clés API dans le fichier .env. "
                "En attendant, je reste disponible pour toutes vos commandes locales : domotique, heure, calculs, et bien plus encore !"
            )
        return "Quota API dépassé, Monsieur. Mes capacités de réflexion sont temporairement limitées."
    finally:
        is_thinking = False
        await send_web_state("idle")

async def demander_ia_vision(texte, img_b64):
    """Analyse une image (capture d'écran) avec Gemini Vision."""
    global is_thinking, historique
    if not gemini_actif or client is None:
        return "La vision nécessite une clé Gemini valide. Configurez-la dans le fichier .env."
    is_thinking = True
    await send_web_state("thinking")
    try:
        print("[VISION] Analyse de l'image avec Gemini...")
        
        # Conversion base64 en bytes pour l'API
        img_bytes = base64.b64decode(img_b64)
        image_part = types.Part.from_bytes(
            data=img_bytes,
            mime_type="image/jpeg"
        )
        
        # Recherche de souvenirs
        souvenirs = rechercher_souvenirs(texte)
        prompt_actuel = construire_system_prompt(souvenirs=souvenirs) + "\n\nIMPORTANT: Réponds uniquement avec le texte de la réponse, n'utilise JAMAIS de format JSON ou de balises structurées. Analyse l'image et réponds."
        
        # On envoie l'image et le texte avec retry en cas de 503
        contents = [
            types.Content(role="user", parts=[image_part, types.Part(text=texte)])
        ]
        
        rep = None
        last_err = None
        for model_name in MODELS_LIST:
            print(f"[VISION] Essai modele : {model_name}")
            for attempt in range(2): # 2 tentatives par modele
                try:
                    print(f"[VISION] Appel modele : {model_name} (Timeout 15s)")
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            client.models.generate_content,
                            model=model_name,
                            config=types.GenerateContentConfig(
                                system_instruction=prompt_actuel,
                                temperature=0.7,
                                tools=[types.Tool(google_search=types.GoogleSearch())],
                            ),
                            contents=contents
                        ),
                        timeout=15.0
                    )
                    rep = response.text
                    break
                except Exception as e:
                    if ("503" in str(e) or "overloaded" in str(e).lower()) and attempt < 1:
                        print(f"[VISION] Surcharge {model_name} (503). Retente...")
                        await asyncio.sleep(1)
                        continue
                    print(f"[VISION] Erreur {model_name} : {e}")
                    last_err = e
                    break
            if rep: break
        
        if not rep:
            err_str = str(last_err).lower() if last_err else ""
            if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                print("[VISION] Quota Gemini epuise — vision impossible sans Gemini.")
                return ("Désolé mylane, mon quota Gemini est épuisé pour aujourd'hui. "
                        "La vision par caméra et écran fonctionne uniquement avec Gemini — "
                        "je ne peux donc pas analyser d'images en ce moment. "
                        "Réessayez demain quand le quota sera réinitialisé.")
            print("[VISION] Tous les modeles Gemini ont echoue. Bascule sur Grok (Texte uniquement)...")
            if grok_client:
                return await demander_grok(texte + " (Note: Je n'ai pas pu voir ton écran car mes serveurs de vision sont indisponibles, je réponds donc uniquement à ton texte).")
            raise last_err or Exception("Aucun modele n'a pu analyser l'image")

        # On ajoute la trace dans l'historique (sans l'image pour éviter de saturer la mémoire)
        historique.append(types.Content(role="user", parts=[types.Part(text=f"[Analyse d'écran] {texte}")]))
        historique.append(types.Content(role="model", parts=[types.Part(text=rep)]))
        
        return rep
    except Exception as e:
        print(f"[VISION] Erreur Gemini Vision : {e}")
        # On évite les accolades dans le message d'erreur pour ne pas perturber l'extracteur JSON
        err_msg = str(e).replace("{", "[").replace("}", "]")
        return f"Désolé mylane, je n'ai pas pu analyser votre écran. Erreur : {err_msg}"
    finally:
        is_thinking = False
        await send_web_state("idle")

def detecter_cerveau(texte):
    # Heuristique pour basculer sur Grok uniquement pour X/Twitter
    mots_cles_grok = ["sur x", "twitter", "grok", "elon", "x.com"]
    cmd = texte.lower()
    if any(m in cmd for m in mots_cles_grok):
        return "GROK"
    return "GEMINI"

async def demander_grok(texte, update_hist=True):
    if not grok_client:
        return None
    
    try:
        # SYNC : On utilise le même prompt système que Gemini (incluant la mémoire)
        souvenirs = rechercher_souvenirs(texte)
        system_prompt = construire_system_prompt(souvenirs=souvenirs)
        messages = [{"role": "system", "content": system_prompt}]
        
        for h in historique[-30:]: # Limiter aux 30 derniers messages
            role = "user" if h.role == "user" else "assistant"
            msg_text = h.parts[0].text
            messages.append({"role": role, "content": msg_text})
        
        messages.append({"role": "user", "content": texte})
        
        completion = grok_client.chat.completions.create(
            model="grok-3", 
            messages=messages,
            temperature=0.7,
        )
        
        rep = completion.choices[0].message.content
        
        # On synchronise l'historique Gemini
        if update_hist:
            historique.append(types.Content(role="user", parts=[types.Part(text=texte)]))
            historique.append(types.Content(role="model", parts=[types.Part(text=rep)]))
            _sauvegarder_echange_conv(texte, rep)
            ajouter_souvenir(texte, rep)
        
        return rep
    except Exception as e:
        if _quota_mgr.is_quota_error(e):
            _quota_mgr.mark_quota_exceeded("grok")
            raise _QuotaExceededError(f"Grok quota: {e}")
        print(f"[ERREUR GROK] {e}")
        return None

async def demander_ollama(texte, update_hist=True):
    """Appelle un modèle local via Ollama (100% offline)."""
    global historique
    try:
        # SYNC : On utilise le même prompt système que Gemini (incluant la mémoire)
        souvenirs = rechercher_souvenirs(texte)
        system_prompt = construire_system_prompt(souvenirs=souvenirs) + "\n\nIMPORTANT: Réponds uniquement avec le texte de la réponse, n'utilise JAMAIS de format JSON."
        messages = [{"role": "system", "content": system_prompt}]
        
        # Optimisation : On limite à 16 entrées (8 échanges complets) pour Ollama afin de rester fluide et rapide
        for h in historique[-16:]:
            role = "user" if h.role == "user" else "assistant"
            messages.append({"role": role, "content": h.parts[0].text})
        messages.append({"role": "user", "content": texte})
        
        last_err = None
        for model_name in OLLAMA_MODELS:
            try:
                print(f"[OLLAMA] Essai modele local : {model_name}")
                resp = await asyncio.wait_for(
                    asyncio.to_thread(
                        requests.post,
                        f"{OLLAMA_URL}/api/chat",
                        json={
                            "model": model_name,
                            "messages": messages,
                            "stream": False,
                            "keep_alive": -1
                        },
                        timeout=30
                    ),
                    timeout=35.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    rep = data.get("message", {}).get("content", "")
                    if rep:
                        historique.append(types.Content(role="user", parts=[types.Part(text=texte)]))
                        historique.append(types.Content(role="model", parts=[types.Part(text=rep)]))
                        _sauvegarder_echange_conv(texte, rep)
                        ajouter_souvenir(texte, rep)
                        print(f"[OLLAMA] Reponse recue de {model_name}")
                        return rep
                else:
                    print(f"[OLLAMA] Erreur HTTP {resp.status_code} pour {model_name}")
                    last_err = Exception(f"HTTP {resp.status_code}")
            except Exception as e:
                print(f"[OLLAMA] Echec {model_name} : {e}")
                last_err = e
                continue
        
        print(f"[OLLAMA] Tous les modeles locaux ont echoue")
        return None
    except Exception as e:
        print(f"[ERREUR OLLAMA] {e}")
        return None

async def demander_groq(texte, update_hist=True, skip_local=False):
    """Appelle Groq (Llama 3.3) avec streaming de parole à la volée (vitesse extrême)."""
    global historique, _derniere_reponse_streamed, phrases_streamed
    if not groq_client:
        return None

    def safe_next(iterator):
        try:
            return next(iterator)
        except StopIteration:
            return None

    try:
        # Recherche de souvenirs
        souvenirs = rechercher_souvenirs(texte)
        system_prompt = construire_system_prompt(souvenirs=souvenirs)
        messages = [{"role": "system", "content": system_prompt}]
        
        for h in historique[-30:]:
            role = "user" if h.role == "user" else "assistant"
            messages.append({"role": role, "content": h.parts[0].text})
            
        messages.append({"role": "user", "content": texte})

        # Démarrage de la complétion en mode streaming
        stream = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            stream=True
        )

        full_text = ""
        sentence_buffer = ""
        iterator = iter(stream)

        while True:
            chunk = await asyncio.to_thread(safe_next, iterator)
            if chunk is None:
                break

            chunk_text = chunk.choices[0].delta.content or ""
            full_text += chunk_text
            sentence_buffer += chunk_text

            if not skip_local and '{' not in full_text:
                # 1. Découpage sur ponctuation forte (suivie d'un espace ou saut de ligne) ou double saut de ligne
                if any(re.search(p, sentence_buffer) for p in [r'\. ', r'\.\n', r'\! ', r'\!\n', r'\? ', r'\?\n', r'\; ', r'\;\n', r'\: ', r'\:\n', r'\n\n']):
                    _derniere_reponse_streamed = True
                    parts = re.split(r'(\.(?: |\n)|\!(?: |\n)|\?(?: |\n)|\;(?: |\n)|\:(?: |\n)|\n\n)', sentence_buffer)
                    for i in range(0, len(parts)-1, 2):
                        phrase = parts[i] + parts[i+1]
                        if phrase.strip():
                            parler(phrase.strip())
                            phrases_streamed.append(phrase.strip())
                    sentence_buffer = parts[-1]
                # 2. Sécurité de longueur : si la phrase est longue, on coupe à 60 caractères pour lancer la synthèse
                elif len(sentence_buffer) > 60 and sentence_buffer.endswith(' '):
                    _derniere_reponse_streamed = True
                    parler(sentence_buffer.strip())
                    phrases_streamed.append(sentence_buffer.strip())
                    sentence_buffer = ""

        if update_hist:
            historique.append(types.Content(role="user", parts=[types.Part(text=texte)]))
            historique.append(types.Content(role="model", parts=[types.Part(text=full_text)]))
            _sauvegarder_echange_conv(texte, full_text)
            ajouter_souvenir(texte, full_text)

        # Lire la phrase finale restante
        if not skip_local and '{' not in full_text and sentence_buffer.strip():
            _derniere_reponse_streamed = True
            parler(sentence_buffer.strip())
            phrases_streamed.append(sentence_buffer.strip())

        return full_text
    except Exception as e:
        if _quota_mgr.is_quota_error(e):
            _quota_mgr.mark_quota_exceeded("groq")
            raise _QuotaExceededError(f"Groq quota: {e}")
        print(f"[ERREUR GROQ] {e}")
        return None

async def demander_claude(texte, update_hist=True):
    """Appelle Claude (Anthropic) — agent IA principal (priorité 0)."""
    if not anthropic_client:
        return None
    try:
        # Recherche de souvenirs
        souvenirs = rechercher_souvenirs(texte)
        system_prompt = construire_system_prompt(souvenirs=souvenirs)
        
        # Conversion historique Gemini → format Anthropic
        messages = []
        for h in historique[-30:]:
            role = "user" if h.role == "user" else "assistant"
            messages.append({"role": role, "content": h.parts[0].text})
        messages.append({"role": "user", "content": texte})

        message = await asyncio.wait_for(
            asyncio.to_thread(
                anthropic_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_prompt,
                messages=messages
            ),
            timeout=15.0
        )
        rep = str(message.content[0].text)

        # Sync historique global
        if update_hist:
            historique.append(types.Content(role="user", parts=[types.Part(text=texte)]))
            historique.append(types.Content(role="model", parts=[types.Part(text=rep)]))
            _sauvegarder_echange_conv(texte, rep)
            ajouter_souvenir(texte, rep)

        return rep
    except Exception as e:
        if _quota_mgr.is_quota_error(e):
            _quota_mgr.mark_quota_exceeded("claude")
            raise _QuotaExceededError(f"Claude quota: {e}")
        print(f"[ERREUR CLAUDE] {e}")
        return None

async def action_whatsapp_appel(contact):
    try:
        parler(f"J'appelle {contact} sur WhatsApp, mylane.")
        # Lancement de l'app via le protocole
        os.system("start whatsapp://")
        time.sleep(6) # On laisse le temps a l'app de s'ouvrir et se focuser
        
        # Recherche du contact (Ctrl+F)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        pyautogui.typewrite(contact)
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(3) # On attend que la conversation s'affiche bien
        
        # Utilisation du raccourci clavier officiel pour l'appel audio (plus fiable que la vision)
        print(f"[WHATSAPP] Envoi du raccourci d'appel (Ctrl+Shift+C)...")
        pyautogui.hotkey('ctrl', 'shift', 'c')
        
        # On ajoute quand meme un petit clic de vision en secours si le raccourci ne suffit pas
        time.sleep(2)
        print(f"[WHATSAPP] Verification par vision au cas ou...")
        await jarvis_vision_cliquer("clique sur le bouton 'Appel vocal' ou l icone de telephone qui vient de s afficher en haut a droite")
        
        return True
    except Exception as e:
        print(f"[WHATSAPP ERROR] {e}")
        parler(f"Desole mylane, je n'ai pas pu lancer l'appel WhatsApp. {e}")
        return False

async def resoudre_commandes_locales(texte):
    """Détecte et exécute les commandes locales (Spotify, dossiers, apps) sans IA."""
    global attente_nom_dossier, attente_nom_app
    t = texte.lower().strip()
    global VOIX_ACTUELLE

    # S'il s'agit d'une commande complexe avec des enchaînements ou des actions DOM/saisie,
    # on renvoie None pour laisser le "cerveau" IA (LLM) s'en occuper de façon autonome.
    if any(k in t for k in ["saisis", "clique", "tape", "ecris", "ecrit", "remplace", "dans la", "barre de", " et ", " puis "]):
        return None

    # --- TEST CARTES CONTEXTUELLES ---
    if ("carte" in t and "test" in t) or "affiche une carte" in t:
        await envoyer_carte_contextuelle(
            "Test Protocole", 
            "Ceci est une carte de test générée par le système contextuel. Tous les capteurs sont opérationnels.",
            type_carte="info",
            icon="◈"
        )
        return "Carte de test affichée sur le HUD, mylane."

    # --- CHANGEMENT DE VOIX ---
    if any(kw in t for kw in ["prends la voix d'homme", "prends la voix de l'homme", "voix d'homme", "voix masculine"]):
        if VOIX_ACTUELLE == "homme":
            return "Ma voix est déjà configurée sur le mode masculin, mylane."
        VOIX_ACTUELLE = "homme"
        return "Très bien Monsieur, je reprends ma voix habituelle."
    
    if any(kw in t for kw in ["prends la voix de femme", "prends la voix d'une femme", "voix de femme", "voix féminine"]):
        if VOIX_ACTUELLE == "femme":
            return "Ma voix est déjà configurée sur le mode féminin, mylane."
        VOIX_ACTUELLE = "femme"
        return "C'est entendu mylane, je passe sur une fréquence vocale féminine."


    # --- GESTION DU CONTEXTE MULTI-TOURS ---
    if attente_nom_dossier:
        t = f"ouvre le dossier {t}"
        attente_nom_dossier = False
    elif attente_nom_app:
        t = f"ouvre l'application {t}"
        attente_nom_app = False
    else:
        # Interception des commandes incompletes
        if t in ["ouvre le dossier", "ouvre mon dossier", "ouvre un dossier"]:
            attente_nom_dossier = True
            return "Quel dossier voulez-vous ouvrir, mylane ?"
        elif t in ["ouvre l'application", "lance l'application", "ouvre le logiciel", "lance le logiciel", "ouvre", "lance"]:
            attente_nom_app = True
            return "Quelle application voulez-vous lancer, mylane ?"

    # --- IDENTITE / CREATEUR (Priorite 0) ---
    _createur_questions = [
        "qui est ton créateur", "qui est ton createur",
        "qui t'a créé", "qui t'a cree", "qui t'a crée",
        "qui ta créé", "qui ta cree", "qui ta crée",
        "qui t'a fabriqué", "qui t'a fabrique",
        "qui t'a inventé", "qui t'a invente",
        "qui t'a construit", "qui ta construit",
        "qui t'a développé", "qui t'a developpe",
        "qui t'a programmé", "qui t'a programme",
        "qui t'a codé", "qui t'a code",
        "qui t'a conçu", "qui t'a concu",
        "qui ta développé", "qui ta developpe",
        "qui ta programmé", "qui ta programme",
        "qui ta codé", "qui ta code",
        "qui ta conçu", "qui ta concu",
        "c'est qui ton créateur", "c'est qui ton createur",
        "t'as été créé par qui", "t'as ete cree par qui",
        "t'es fait par qui", "tu es fait par qui",
        "tu viens d'où", "tu viens d'ou", "tu viens de ou",
        "d'où tu viens", "d'ou tu viens",
        "qui est derrière toi", "qui est derriere toi",
        "qui est ton père", "qui est ton pere",
        "qui est ton papa",
        "qui est ton développeur", "qui est ton developpeur",
        "qui est ton dev",
        "ton créateur c'est qui", "ton createur c'est qui",
    ]
    if any(q in t for q in _createur_questions):
        import random as _rnd
        _reponses_createur = [
            "J'ai été créé par mylane. C'est grâce à lui que j'existe aujourd'hui.",
            "Mon créateur, c'est Mylane. Il m'a conçu de A à Z pour être votre assistant personnel.",
            "Je suis le fruit du travail de Mylane. Tout mon code, ma voix, mon intelligence, c'est lui.",
            "Mylane est mon créateur. C'est lui qui m'a donné vie, et je dois dire qu'il a fait du bon boulot.",
            "C'est Mylane qui m'a développé. Un développeur passionné qui voulait créer l'assistant ultime.",
            "Mon père numérique, c'est Mylane. Il m'a programmé avec passion pour vous aider au quotidien.",
            "Mylane, c'est le génie derrière mon existence.",
            "Je suis né dans les lignes de code de Mylane. Sans lui, je ne serais qu'un écran noir.",
            "Mylane m'a créé. C'est un développeur français qui a voulu rendre l'intelligence artificielle accessible à tous.",
            "Mon créateur s'appelle Mylane. Il a mis tout son savoir-faire pour me construire, et je lui en suis reconnaissant.",
        ]
        return _rnd.choice(_reponses_createur)

    # --- AIDE / CAPACITES (Priorite 0) ---
    _aide_questions = [
        "que peux-tu faire", "que peux tu faire", "que sais-tu faire", "que sais tu faire",
        "quelles sont tes capacités", "quelles sont tes capacites",
        "montre moi tes capacités", "montre-moi tes capacités",
        "montre moi ce que tu sais faire", "aide moi", "aide-moi",
        "montre moi tes commandes", "liste tes commandes", "qu'est-ce que tu peux faire"
    ]
    if any(q in t for q in _aide_questions):
        # Envoi IMMEDIAT de l'action help au frontend
        if CONNECTED_CLIENTS:
            async def _dispatch_help():
                msg = json.dumps({"action": "help"})
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
            asyncio.create_task(_dispatch_help())
        
        import random as _rnd
        _reponses_aide = [
            "J'affiche mes systèmes de bord, mylane. Je peux gérer votre musique, lancer des recherches, naviguer sur le globe 3D, ou encore ouvrir vos dossiers personnels. Que souhaitez-vous tester ?",
            "Déploiement des protocoles d'assistance. Voici mes modules actifs : contrôle média, navigation satellite, recherche intelligente et gestionnaire de fichiers. Je suis à vos ordres.",
            "Bien sûr. Je suis capable de localiser n'importe quel point sur Terre, de piloter vos applications, et de répondre à vos questions complexes. Jetez un œil aux suggestions à l'écran.",
            "Initialisation de l'interface d'aide. Je peux aussi bien prendre une capture d'écran que vous donner la météo à l'autre bout du monde. Dites-moi simplement ce qu'il vous faut.",
            "Accès aux bases de données. Je peux automatiser vos tâches répétitives, gérer vos rappels et même vous raconter une blague si l'ambiance est trop sérieuse.",
        ]
        return _rnd.choice(_reponses_aide)

    # --- DOSSIERS (Priorité 1) ---
    if any(k in t for k in ["mosaïque dossiers", "range mes dossiers", "range les dossiers", "range tous les dossiers", "range tous mes dossiers", "mosaïque"]):
        return arranger_fenetres_dossiers()

    # --- MODE EXPLORATEUR SPATIAL 3D ---
    if any(k in t for k in [
        "ouvre tous les dossiers", "ouvre tous mes dossiers", "ouvre mes dossiers", "ouvre les dossiers", 
        "mes dossiers", "montre moi mes dossiers", "montre mes dossiers", "explorateur 3d", "explorateur spatial", 
        "dossier spatial", "explorateur spatial 3d", "mode explorer", "affiche l'explorateur", 
        "ouvre l'explorateur spatial", "affiche mes fichiers"
    ]):
        _safe_ws_send(json.dumps({"action": "open_spatial_explorer"}))
        return "Déploiement de l'explorateur spatial 3D, mylane."

    # --- MODE CARTE 3D DOMOTIQUE ---
    if any(k in t for k in [
        "affiche ma maison", "affiche la maison", "carte domotique", "mode carte 3d", "mode carte", 
        "carte 3d", "affiche la carte 3d", "affiche la carte de la maison", "affiche la carte domotique", 
        "ma maison 3d"
    ]):
        _safe_ws_send(json.dumps({"action": "open_domotic_map"}))
        return "Déploiement de la carte domotique 3D, mylane."

    # --- RECHERCHE SÉMANTIQUE VISUELLE CORTEX ---
    if any(p in t for p in ["cherche dans mon cortex", "cherche dans le cortex", "trouve dans mon cortex", "trouve dans le cortex"]):
        query = t
        for prefix in ["cherche dans mon cortex", "cherche dans le cortex", "trouve dans mon cortex", "trouve dans le cortex"]:
            if prefix in query:
                query = query.replace(prefix, "").strip()
        query = query.replace("?", "").strip()
        if len(query) > 1:
            _safe_ws_send(json.dumps({"action": "cortex_search", "query": query}))
            return f"Recherche de '{query}' initiée dans mon cortex neuronal, mylane."
        return "Que souhaitez-vous chercher dans votre cortex, mylane ?"

    # --- MODE CORTEX 3D ---
    if any(k in t for k in [
        "cortex", "affiche ton cortex", "affiche le cortex", "mode cortex", "ouvre le cortex", 
        "ouvre ton cortex", "connexions neuronales", "cortex neuronal"
    ]):
        _safe_ws_send(json.dumps({"action": "open_cortex"}))
        return "Déploiement du cortex neuronal 3D, mylane."

    # --- NARRATION VOCALE DE SOUVENIR ---
    if any(p in t for p in ["lis ce souvenir", "raconte ce souvenir", "lis la mémoire", "raconte cette mémoire", "lis le souvenir"]):
        _safe_ws_send(json.dumps({"action": "cortex_vocal_speak_request"}))
        return "C'est entendu, mylane. Lecture du souvenir actif..."

    # --- DECLENCHEMENT PROTOCOLE DEMONSTRATION ORBE ---
    if any(k in t for k in ["démonstration", "demonstration", "démo", "demo", "lance la démo", "lance une démo", "lance une démonstration", "lance la démonstration", "protocole de démo", "fais une démo", "fais une demo"]):
        _safe_ws_send(json.dumps({"action": "demo"}))
        return "Initialisation du protocole de démonstration visuelle, mylane."

    # --- GÉNÉRATION D'IMAGES (Priorité 0.5) ---
    if any(k in t for k in ["génère", "genere", "crée une image", "cree une image", "dessine"]):
        import re
        # On supprime toutes les expressions qui servent à demander l'image
        prompt = re.sub(r'(jarvis|génère(-moi| moi|)?|genere(-moi| moi|)?|crée|cree|dessine(-moi| moi|)?)( une| l\'| des| de l\'|) ?(image|photo|dessin|illustration)? ?(de |d\'|d\'une |d\'un |des )?', '', t).strip()
        
        if prompt:
            parler(f"Très bien mylane, je génère l'image de {prompt}. Un instant...")
            img_data = generer_image_ia(prompt)
            if img_data:
                await envoyer_image_web(img_data, prompt)
                return f"Voici l'image demandée, mylane. Elle s'affiche sur votre interface."
            return "Désolé mylane, la génération d'image a échoué."
        return "Que souhaitez-vous que je dessine, mylane ?"

    prefixes_dossiers = ["ouvre le dossier ", "ouvre mon dossier ", "ouvre le répertoire ", "ouvre le repertoire ", "ouvre dossier ", "ouvre ", "mets "]
    # On vérifie d'abord si c'est un dossier connu
    mots_cles_dossiers = ["bureau", "document", "téléchargement", "image", "photo", "vidéo", "musique", "corbeille"]
    # --- LOGIQUE MULTIMÉDIA (TV/YouTube) MIGRÉE VERS plugins/system_resolver.py ---

    # --- DOSSIERS (Priorité 1) ---
    for prefix in prefixes_dossiers:
        if t.startswith(prefix):
            potentiel_dossier = t.replace(prefix, "").strip()
            if any(k in potentiel_dossier for k in mots_cles_dossiers):
                ok, msg = ouvrir_dossier(potentiel_dossier)
                if ok: return f"J'ouvre le dossier {potentiel_dossier}, mylane."

    # --- MODE BOULOT (Priorité 1 bis) ---
    if any(k in t for k in ["au boulot", "mode boulot", "mode travail", "on bosse", "mode bureau", "commence le boulot"]):
        return await mode_boulot()

    # (Le bloc TV est désormais en haut)

    if any(k in t for k in ["mode gaming", "mode jeu", "on joue", "session gaming", "lance le gaming", "mode gamer"]):
        return await mode_gaming()

    if any(k in t for k in ["mode rocket league", "lance rocket league", "joue à rocket league", "on joue à rocket league"]):
        return await mode_rocket_league()

    # --- APPLICATIONS STANDARD & CATALOGUE (Priorité 2) ---
    # IMPORTANT : ces checks doivent être AVANT la détection Spotify car
    # "lance " est aussi un préfixe Spotify → "lance steam" partirait sinon vers Spotify.
    mots_ouvrir = ["ouvre", "lance", "démarre", "démarres", "ouvrir", "lancer"]
    mots_fermer = ["ferme", "quitte", "stoppe", "éteins", "coupe", "fermer", "quitter"]

    apps_standard = {
        "calculatrice":            "calc",
        "notepad":                 "notepad",
        "bloc-notes":              "notepad",
        "bloc notes":              "notepad",
        "paint":                   "mspaint",
        "gestionnaire de tâches":  "taskmgr",
        "gestionnaire de taches":  "taskmgr",
        "task manager":            "taskmgr",
        "panneau de configuration": "control",
        "paramètres":              "ms-settings:",
        "parametres":              "ms-settings:",
        "réglages":                "ms-settings:",
        "reglages":                "ms-settings:",
        "explorateur":             "explorer",
        "explorateur de fichiers": "explorer",
        "invite de commande":      "cmd",
        "cmd":                     "cmd",
        "snipping tool":           "SnippingTool",
        "outil capture":           "SnippingTool",
        "capture d'écran":         "SnippingTool",
        "capture d'ecran":         "SnippingTool",
        "enregistreur vocal":      "SoundRecorder",
        "magnétophone":            "SoundRecorder",
        "table des caractères":    "charmap",
        "caractères spéciaux":     "charmap",
        "nettoyage de disque":     "cleanmgr",
        "informations système":    "msinfo32",
        "info système":            "msinfo32",
        "info systeme":            "msinfo32",
    }
    for nom, cmd in apps_standard.items():
        if any(f"{m} {nom}" in t for m in mots_ouvrir):
            try:
                subprocess.Popen(cmd)
                return f"J'ouvre {nom}, mylane."
            except Exception:
                return f"Désolé mylane, je n'ai pas réussi à lancer {nom}."

    import re
    for cle, info in _APPS_CATALOGUE.items():
        # On vérifie que la clé est un mot entier pour éviter "ea" dans "Billie Jean"
        if not re.search(rf"\b{re.escape(cle)}\b", t):
            continue
            
        if any(m in t for m in mots_fermer):
            ok = _fermer_app(info["noms"])
            if ok:
                return f"J'ai fermé {info['label']}, mylane."
            return f"Je n'ai pas trouvé {info['label']} en cours d'exécution."
        if any(m in t for m in mots_ouvrir):
            _boulot_lancer(info["label"], info["noms"], chemins_hints=info["hints"])
            return f"Je lance {info['label']}, mylane."

    # (Bloc YouTube PC supprimé pour éviter les conflits avec la TV)

    # --- SPOTIFY / MUSIQUE (Priorité 3) ---
    # YouTube music spécifique — doit être AVANT le check Spotify
    if any(k in t for k in ["musique sur youtube", "met de la musique sur youtube", "mets de la musique sur youtube"]):
        url = YOUTUBE_MUSIQUE_URL or "https://www.youtube.com/watch?v=Cr8K88UcO0s"
        webbrowser.open(url, new=2)
        time.sleep(5)
        pyautogui.press('f')
        return "C'est parti mylane, je lance votre musique sur YouTube."

    # Playlist de musique par défaut — intelligente (Deezer, YouTube, Spotify ou personnalisé)
    if any(k in t for k in [
        "met de la musique", "mets de la musique",
        "lance ma playlist", "ma playlist"
    ]):
        # Extraire la requête spécifique de musique/playlist
        # Si l'utilisateur a spécifié un nom (ex: "joue ma playlist teenage dirtbag"),
        # on ne traite pas cela comme le lancement de la playlist par défaut.
        query_normalized = t
        for verb in ["joue", "jouer", "mets", "mettre", "lance", "lancer", "écoute", "ecoute", "écouter", "ecouter", "play", "active", "activer", "démarre", "demarre", "démarrer", "demarrer"]:
            query_normalized = re.sub(rf"\b{verb}\b", "", query_normalized)
        for article in ["ma", "la", "mon", "le", "un", "une", "des", "du", "de", "de la", "d'", "votre", "notre", "mes", "les", "moi"]:
            query_normalized = re.sub(rf"\b{article}\b", "", query_normalized)
        for noun in ["musique", "playlist", "chanson", "piste", "titre", "album", "artiste", "son"]:
            query_normalized = re.sub(rf"\b{noun}\b", "", query_normalized)
        
        specific_query = query_normalized.strip()
        if not specific_query:
            import json as _j
            musique_lien = None
            try:
                _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_config.json")
                if os.path.exists(_p):
                    with open(_p, "r", encoding="utf-8") as _f:
                        cfg_temp = _j.load(_f)
                        musique_lien = cfg_temp.get("musique_lien")
            except: pass

            if musique_lien:
                musique_lien_lower = musique_lien.lower()
                if "youtube.com" in musique_lien_lower or "youtu.be" in musique_lien_lower:
                    webbrowser.open(musique_lien, new=2)
                    time.sleep(5)
                    pyautogui.press('f')
                    return "C'est parti mylane, je lance votre musique sur YouTube."
                elif "spotify" in musique_lien_lower or musique_lien_lower.startswith("spotify:"):
                    try:
                        from controller.spotify_controller import spotify_lancer_playlist
                        ok = spotify_lancer_playlist(musique_lien)
                        if ok:
                            return "C'est parti mylane, je lance votre musique sur Spotify."
                    except: pass
                    return "Je n'ai pas réussi à ouvrir Spotify, mylane."
                elif "deezer" in musique_lien_lower:
                    ok = await deezer_lancer_playlist(musique_lien)
                    if ok:
                        return "C'est parti mylane, je lance votre musique sur Deezer."
                    return "Je n'ai pas réussi à ouvrir Deezer, mylane."
                else:
                    # Lien générique
                    webbrowser.open(musique_lien, new=2)
                    return "C'est parti mylane, je lance votre lien de musique personnalisé dans le navigateur."
            else:
                # Fallback par défaut sur Deezer
                ok = await deezer_lancer_playlist()
                if ok:
                    return "C'est parti mylane, je lance votre playlist sur Deezer."
                return "Je n'ai pas réussi à ouvrir Deezer, mylane."

    if any(k in t for k in ["ouvre deezer", "lance deezer"]):
        return await deezer_ouvrir()

    if any(k in t for k in ["suivante", "suivant", "chanson suivante", "piste suivante", "morceau suivant", "musique suivante", "musique d'après", "musique d'apres"]):
        return await deezer_suivant()
    if any(k in t for k in ["précédente", "précédent", "precedente", "precedent", "chanson précédente", "morceau précédent", "reviens en arrière", "retour en arrière", "musique d'avant"]):
        return await deezer_precedent()
    if any(k in t for k in ["mets en pause", "stop la musique", "arrête la musique", "arrete la musique", "arrête la playlist", "arrete la playlist", "mets sur pause", "met en pause", "met sur pause", "met pause", "mets pause", "pause"]):
        return await deezer_stop()
    if any(k in t for k in ["lecture", "remets la musique", "remet la musique", "reprends la musique", "reprend la musique", "relance la musique", "relance la playlist", "lance la musique", "joue la musique", "remets la playlist", "remet la playlist"]):
        return await deezer_lecture_pause()
    if any(k in t for k in ["monte le volume", "augmente le son", "plus fort"]):
        return await deezer_volume("monter")
    if any(k in t for k in ["baisse le son", "baisse le volume", "moins fort"]):
        return await deezer_volume("baisser")

    # Recherche Deezer générique — en dernier pour ne pas avaler les commandes apps
    prefixes_recherche = ["joue du ", "joue de la ", "mets du ", "mets de la ", "joue ", "recherche ", "mets ", "lance ", "écoute ", "ecoute "]
    for prefix in prefixes_recherche:
        # On évite de chercher sur Deezer si c'est manifestement une recherche de fichier local
        if t.startswith(prefix) and not any(k in t for k in ["dossier", "fichier", "document", "ordinateur", "pc"]):
            recherche = t.replace(prefix, "").replace(" sur deezer", "").strip()
            if len(recherche) > 1:
                return await deezer_rechercher(recherche)

    raccourcis_dossiers = {
        "bureau": "bureau", "documents": "documents",
        "téléchargements": "downloads", "téléchargement": "downloads",
        "images": "images", "vidéos": "videos", "musique": "musique"
    }
    for cle, chemin in raccourcis_dossiers.items():
        if f"ouvre mon {cle}" in t or f"ouvre le {cle}" in t or t == f"ouvre {cle}":
            ouvrir_dossier(chemin)
            return f"J'ouvre votre dossier {cle}, mylane."

    # --- DOSSIER / APPLICATION INCONNU(E) ---
    # Si l'utilisateur demande d'ouvrir/lancer quelque chose qu'on ne connait pas
    _mots_action = ["ouvre ", "lance ", "démarre ", "démarres ", "ouvrir ", "lancer ", "ouvre le ", "ouvre la ",
                     "ouvre mon ", "ouvre ma ", "lance le ", "lance la ", "lance mon ", "lance ma ",
                     "ouvre le dossier ", "ouvre mon dossier ", "ouvre l'application ", "lance l'application ",
                     "ouvre l'appli ", "lance l'appli ", "ouvre le logiciel ", "lance le logiciel "]
    for mot in _mots_action:
        if t.startswith(mot):
            nom_demande = t.replace(mot, "").strip().rstrip(".")
            if len(nom_demande) > 1:
                import random as _rnd
                _reponses_inconnu = [
                    f"Désolé mylane mon créateur n'a pas encore ajouté \"{nom_demande}\" dans mes fonctionnalités. Mais vous pouvez l'ajouter vous-même gratuitement avec le logiciel Antigravity de chez Google.",
                    f"Je ne connais pas \"{nom_demande}\" pour l'instant, mylane, mon développeur, n'a pas intégré cette fonction. Cependant, vous pouvez la créer facilement avec Antigravity de Google, c'est gratuit.",
                    f"Hmm, \"{nom_demande}\" ne fait pas partie de mes compétences actuelles. Mon créateur Mylane pourra peut-être l'ajouter dans une future mise à jour. En attendant, essayez Antigravity de Google pour personnaliser vos commandes gratuitement.",
                    f"\"{nom_demande}\" n'est pas dans ma base de données, mylane, n'a pas encore programmé cette action. Bonne nouvelle : avec Antigravity de chez Google, vous pouvez l'ajouter vous-même sans frais.",
                    f"Je ne suis pas encore capable d'ouvrir \"{nom_demande}\", mylane, mon créateur travaille constamment à m'améliorer. En attendant, le logiciel Antigravity de Google vous permet d'étendre mes fonctionnalités gratuitement.",
                    f"Cette fonctionnalité n'a pas été ajoutée par Mylane, mon créateur. Mais ne vous inquiétez pas, mylane, vous pouvez utiliser Antigravity de chez Google pour ajouter \"{nom_demande}\" gratuitement.",
                ]
                return _rnd.choice(_reponses_inconnu)

    return None

def est_action_oriented(texte):
    t = texte.lower()
    mots_actions = [
        "oublie", "oublier", "supprime", "supprimer", "efface", "effacer", "vide", "vider", "annule", "annuler", "retire", "retirer",
        "met", "alarme", "reveil", "réveil", "minuteur", "lance", "joue", "ouvre", "ferme", "éteins", "allume", "active", "désactive",
        "spotify", "deezer", "trie", "crée", "creer", "renomme", "déplace", "cherche", "recherche", "analyse", "weather", "météo", "meteo",
        "ajoute", "ajouter", "tâche", "tache", "valide", "valider", "complete", "completer", "termine", "terminer", "drive",
        "envoie", "envoyer", "réponds", "repondre", "reponds", "agenda", "calendrier", "partage", "partager", "tableur", "ligne",
        "cellule", "mail", "email", "courriel", "doc", "document", "téléverse", "televerse", "téléverser", "televerser", "charge",
        "charger", "dossier", "sheet", "sheets", "docs"
    ]
    return any(m in t for m in mots_actions)

async def traiter_reponse_ia(texte_utilisateur, mobile_ws=None, from_voice=False):
    global MODE_IRON_MAN, jarvis_actif, dernier_message, _skip_pc_audio, is_thinking, _derniere_reponse_streamed, phrases_streamed, ACTIVE_SPEAKER
    dernier_message = time.time()
    _derniere_reponse_streamed = False
    phrases_streamed = []
    if from_voice:
        jarvis_actif = True  # Seules les commandes vocales ouvrent/maintiennent la session
    else:
        # Saisie clavier/écrite : l'utilisateur physique est toujours détecté comme "mylane"
        ACTIVE_SPEAKER = "mylane"
        builtins.ACTIVE_SPEAKER = "mylane"

    if traiter_lock.locked():
        parler("Je termine ce que je fais, mylane. Un instant.")
        return

    async with traiter_lock:
        is_thinking = True
        # Reset du flag audio au début de chaque commande
        _skip_pc_audio = False
        
        # NETTOYAGE DU TEXTE (Enlever 'Jarvis' au début pour ne pas perturber les plugins)
        texte_utilisateur = nettoyer_commande(texte_utilisateur)

        # TENTATIVE DE RÉSOLUTION LOCALE (Commandes, Math, Français, etc.)
        print(f"[DEBUG] Tentative de résolution locale pour : {texte_utilisateur}")
        reponse = await builtins.resoudre_developpement(texte_utilisateur)
        
        # Résolution locale dynamique (Pour les résolveurs additionnels enregistrés à chaud sans redémarrage)
        if not reponse:
            for attr_name in sorted(dir(builtins)):
                if attr_name.startswith("resoudre_") and attr_name not in ["resoudre_developpement", "resoudre_dom_hud", "resoudre_chemin"]:
                    try:
                        resolver_fn = getattr(builtins, attr_name)
                        if asyncio.iscoroutinefunction(resolver_fn):
                            reponse = await resolver_fn(texte_utilisateur)
                        else:
                            reponse = resolver_fn(texte_utilisateur)
                        if reponse:
                            print(f"[DEBUG] Commande résolue dynamiquement par : {attr_name}")
                            break
                    except Exception as e:
                        print(f"[DEBUG DYNAMIC] Erreur lors de l'appel du résolveur {attr_name} : {e}")

        if not reponse: reponse = await builtins.resoudre_dom_hud(texte_utilisateur)
        if not reponse: reponse = await resoudre_commandes_locales(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_commandes_systeme(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_tv_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_apps_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_infos_systeme_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_memoire_locale(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_temps_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_listes_locales(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_francais_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_conversion_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_traduction_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_globe_localement(texte_utilisateur)
        if not reponse: reponse = await builtins.resoudre_extras_locaux(texte_utilisateur)
        
        if not reponse:
            force_skip_local = est_action_oriented(texte_utilisateur)
            reponse = await demander_ia(texte_utilisateur, skip_local=force_skip_local)
        
        # print(f"[JARVIS] {reponse}")

        # Si commande mobile : activer le flag pour couper l'audio PC et répondre via mobile
        if mobile_ws:
            _skip_pc_audio = True

        # Robustesse type : Si le résolveur a retourné un booléen, le convertir en chaîne
        if isinstance(reponse, bool):
            reponse = "Commande exécutée." if reponse else ""

        # 1. Extraction robuste des blocs JSON
        def extract_json_blocks(text):
            blocks = []
            stack = []
            start = -1
            for i, char in enumerate(text):
                if char == '{':
                    if not stack: start = i
                    stack.append('{')
                elif char == '}':
                    if stack:
                        stack.pop()
                        if not stack:
                            blocks.append(text[start:i+1])
            return blocks

        json_blocks = extract_json_blocks(reponse)
        reponse_propre = reponse
        for b in json_blocks:
            reponse_propre = reponse_propre.replace(b, "")
        reponse_propre = reponse_propre.strip()

        # Si la réponse contient une action système (autre que auto_memoriser), on supprime la parole conversationnelle
        contient_action_systeme = False
        for block in json_blocks:
            try:
                data = json.loads(block)
                action = data.get("action", "")
                if action and action != "auto_memoriser":
                    contient_action_systeme = True
                    break
            except:
                pass

        # 2. PAROLE (avant d'exécuter les actions pour respecter l'ordre naturel d'énonciation)
        texte_a_parler = "" if contient_action_systeme else reponse_propre
        if texte_a_parler and phrases_streamed:
            for phrase in phrases_streamed:
                phrase_strip = phrase.strip()
                if texte_a_parler.strip().startswith(phrase_strip):
                    idx = texte_a_parler.find(phrase_strip)
                    texte_a_parler = texte_a_parler[idx + len(phrase_strip):].strip()

        if texte_a_parler:
            texte_reel = re.sub(r'[^\w\s]', '', texte_a_parler).strip()
            if texte_reel:
                builtins.parler(texte_a_parler, print_console=True)

        # 3. EXÉCUTION DES ACTIONS
        for block in json_blocks:
            try:
                if any(x in block for x in ["NOM_DU_CONTACT", "VALEUR_ICI", "CLE_ICI", "chemin/complet"]):
                    continue

                print(f"[JARVIS] Execution de l'action : {block}")
                data = json.loads(block)
                action = data.get("action", "")
                
                # Sécurité mode invité : bloquer uniquement les actions définies comme sensibles (fichiers, vision/écrans, Google APIs)
                restricted_actions = {
                    # Fichiers
                    "ouvrir_dossier", "lister_dossier", "trier_par_type", "trier_par_date", 
                    "trier_complet", "creer_dossier", "renommer_fichier", "deplacer_fichier", 
                    "chercher_fichier", "ouvrir_element", "analyser_fichier",
                    # Vision / Screenshots / Autopilot
                    "voir_ecran", "vision_ecrire", "vision_chercher_sur_site", "vision_navigateur",
                    "analyse_live", "web_agent_task",
                    # Google APIs
                    "open_drive", "search_drive", "create_doc", "write_doc", "create_sheet",
                    "read_sheet", "read_doc", "upload_file", "share_file", "create_folder", "append_sheet",
                    "read_emails", "send_email", "reply_email", "read_full_email", "archive_email", "delete_email",
                    "read_calendar", "create_event", "update_event", "delete_event",
                    "create_task", "list_tasks", "complete_task", "delete_task"
                }
                if globals().get("ACTIVE_SPEAKER", "mylane") == "guest" and action in restricted_actions:
                    print(f"🔒 [SPEAKER] Action '{action}' bloquée en mode invité.")
                    parler("Désolé, cette action est restreinte en mode invité. Veuillez vous authentifier.")
                    continue

                if action == "mode_iron_man":
                    MODE_IRON_MAN = (etat == "on")
                    msg = "Mode Iron Man activé, Monsieur. Je reste à l'écoute de vos signaux." if MODE_IRON_MAN else "Mode Iron Man désactivé. Je repasse en veille domotique."
                    parler(msg)
                elif action == "auto_memoriser":
                    cle    = data.get("cle",    "info")
                    valeur = data.get("valeur", "")
                    ajouter_memoire(cle, valeur)
                    if hasattr(builtins, "_notify_factual_memory_added"):
                        builtins._notify_factual_memory_added(cle, valeur)
                elif action == "memoriser":
                    cle    = data.get("cle",    "info")
                    valeur = data.get("valeur", "")
                    ajouter_memoire(cle, valeur)
                    if hasattr(builtins, "_notify_factual_memory_added"):
                        builtins._notify_factual_memory_added(cle, valeur)
                    parler(f"Bien note mylane, je me souviendrai que {valeur}.")
                elif action == "oublier":
                    cle     = data.get("cle", "")
                    # Supprimer de la mémoire clé-valeur
                    success_kv = supprimer_memoire(cle)
                    # Supprimer également de la DB vectorielle
                    from module.vector_memory import supprimer_souvenir_semantique
                    success_vect = supprimer_souvenir_semantique(cle)
                    
                    if success_kv or success_vect:
                        if success_kv:
                            _safe_ws_send(json.dumps({"action": "cortex_update", "deleted_id": f"kv_{cle}"}))
                        if success_vect:
                            _safe_ws_send(json.dumps({"action": "cortex_update", "deleted_id": cle}))
                        parler("Information oubliee, mylane.")
                    else:
                        parler("Je n avais pas cette information en memoire.")
                elif action == "lister_memoire":
                    memoire = charger_memoire()
                    if not memoire:
                        parler("Aucune information personnalisee en memoire, mylane.")
                    else:
                        lignes = ["Voici ce que je sais sur vous mylane."]
                        for cle, data_m in memoire.items():
                            lignes.append(f"{cle} : {data_m['valeur']}.")
                        parler(" ".join(lignes))
                elif action == "generer_image":
                    prompt = data.get("prompt", "")
                    if prompt:
                        parler(f"Très bien mylane, je génère l'image de {prompt}. Un instant...")
                        img_data = generer_image_ia(prompt)
                        if img_data:
                            await envoyer_image_web(img_data, prompt)
                            parler("Voici l'image demandée, mylane. Elle s'affiche sur votre interface.")
                        else:
                            parler("Désolé mylane, la génération d'image a échoué.")
                    else:
                        parler("Que souhaitez-vous que je dessine, mylane ?")
                elif action == "ouvrir_dossier":
                    chemin = data.get("chemin", "bureau")
                    ok, resultat = ouvrir_dossier(chemin)
                    if ok:
                        parler("Dossier ouvert, mylane. Dites-moi si vous voulez que je le trie.")
                    else:
                        parler(f"Je n ai pas trouve ce dossier, mylane. {resultat}")
                elif action == "analyser_fichier":
                    nom = data.get("nom", "")
                    question = data.get("question", "Peux-tu me résumer ce document ?")
                    if nom:
                        parler(f"Je lis le fichier {nom}... Un instant.")
                        texte_fichier, err_ou_chemin = lire_fichier(nom, chemin=data.get("chemin"))
                        if texte_fichier is None:
                            parler(err_ou_chemin)
                        else:
                            prompt_analyse = (
                                f"URGENT : Tu es JARVIS, l'assistant personnel de mylane.\n"
                                f"Tu viens d'extraire le contenu du fichier '{nom}'.\n"
                                f"Voici ce contenu :\n\n{texte_fichier}\n\n"
                                f"L'utilisateur demande : {question}\n"
                                f"Analyse ce contenu et réponds directement en restant dans ton personnage de JARVIS (poli, efficace, un peu sarcastique)."
                            )
                            rep_analyse = await demander_ia(prompt_analyse, update_hist=False, skip_local=True)
                            if rep_analyse:
                                parler(rep_analyse)
                            else:
                                parler("Désolé mylane, j'ai lu le fichier mais je n'arrive pas à synthétiser une réponse.")
                    else:
                        parler("Je n'ai pas compris quel fichier vous souhaitez que j'analyse.")
                elif action == "lister_dossier":
                    contenu, err = lister_dossier()
                    if err:
                        parler(err)
                    else:
                        nb_fichiers = len(contenu["fichiers"])
                        nb_dossiers = len(contenu["dossiers"])
                        parler(f"Le dossier contient {nb_fichiers} fichiers et {nb_dossiers} sous-dossiers, mylane.")
                elif action == "trier_par_type":
                    parler("Je trie vos fichiers par type, mylane. Un instant.")
                    ok, msg = trier_par_type()
                    parler(msg if ok else f"Probleme lors du tri : {msg}")
                elif action == "trier_par_date":
                    parler("Je trie vos fichiers par date, mylane. Un instant.")
                    ok, msg = trier_par_date()
                    parler(msg if ok else f"Probleme lors du tri : {msg}")
                elif action == "trier_complet":
                    parler("Je trie vos fichiers par type puis par date dans chaque categorie, mylane.")
                    ok, msg = trier_par_type_puis_date()
                    parler(msg if ok else f"Probleme lors du tri : {msg}")
                elif action == "creer_dossier":
                    nom     = data.get("nom", "Nouveau Dossier")
                    ok, msg = creer_sous_dossier(nom)
                    parler(msg if ok else f"Erreur : {msg}")
                elif action == "renommer_fichier":
                    ancien  = data.get("ancien", "")
                    nouveau = data.get("nouveau", "")
                    ok, msg = renommer_fichier(ancien, nouveau)
                    parler(msg if ok else f"Erreur : {msg}")
                elif action == "deplacer_fichier":
                    fichier = data.get("fichier",     "")
                    dest    = data.get("destination", "")
                    ok, msg = deplacer_fichier(fichier, dest)
                    parler(msg if ok else f"Erreur : {msg}")
                elif action == "chercher_fichier":
                    nom = data.get("nom", "")
                    
                    # Détection du type demandé AVANT nettoyage
                    type_demande = None
                    if "dossier" in nom.lower() or "repertoire" in nom.lower():
                        type_demande = "dossier"
                    elif "fichier" in nom.lower() or "document" in nom.lower():
                        type_demande = "fichier"

                    # Nettoyage intelligent du nom (suppression des articles et mots parasites)
                    parasites = ["trouve moi le dossier ", "trouve moi le fichier ", "trouve moi le ", 
                                 "recherche le dossier ", "recherche le fichier ", "recherche le ",
                                 "le dossier ", "le fichier ", "un dossier ", "un fichier ",
                                 "dossier ", "fichier ", "mon dossier ", "mon fichier ", 
                                 "le ", "la ", "les ", "un ", "une ", "des ", "moi "]
                    
                    nom_clean = nom.lower()
                    for p in parasites:
                        if nom_clean.startswith(p):
                            nom_clean = nom_clean[len(p):].strip()
                            break
                    
                    # On nettoie encore les petits mots si besoin
                    mots = nom_clean.split()
                    if mots and mots[0] in ["le", "la", "un", "une", "moi", "mon", "ma"]:
                        mots = mots[1:]
                    nom_final = " ".join(mots) if mots else nom_clean
                    if not nom_final: nom_final = nom
                    
                    # Message plus précis
                    type_msg = "le dossier" if type_demande == "dossier" else ("le fichier" if type_demande == "fichier" else "l'élément")
                    parler(f"Recherche de {type_msg} '{nom_final}' en cours...")
                    
                    resultats, err = chercher_fichier(nom_final, scan_global=True, type_cible=type_demande)
                    if err:
                        parler(err)
                    elif not resultats:
                        parler(f"Je n'ai rien trouvé correspondant à '{nom}', mylane.")
                    else:
                        cible = resultats[0]
                        ok, msg = ouvrir_fichier_ou_dossier(cible)
                        if ok:
                            parler(f"J'ai trouvé {os.path.basename(cible)} et je l'ouvre immédiatement.")
                        else:
                            parler(f"J'ai trouvé {os.path.basename(cible)} mais je n'ai pas pu l'ouvrir : {msg}")
                elif action == "ouvrir_element":
                    chemin = data.get("chemin", "")
                    ok, msg = ouvrir_fichier_ou_dossier(chemin)
                    parler(msg if ok else f"Erreur : {msg}")
                elif action == "ha_lumiere":
                    piece      = data.get("piece",      "salon").lower().strip()
                    etat       = data.get("etat",       "on")
                    couleur    = data.get("couleur",    None)
                    luminosite = data.get("luminosite", None)
                    entity_id  = PIECES_LUMIERES.get(piece, f"light.{piece}")
                    rgb        = COULEURS_MAP.get(couleur) if couleur else None
                    ha_lumiere(entity_id, etat, luminosite, rgb)
                    
                    # Message de confirmation amélioré
                    if etat == "off":
                        msg = f"J'éteins {piece}."
                    else:
                        details = []
                        if couleur: details.append(f"en {couleur}")
                        if luminosite is not None: 
                            pourcent = int((int(luminosite)/255)*100)
                            details.append(f"à {pourcent}%")
                        
                        if details:
                            msg = f"C'est fait, {piece} est réglé{' '.join(details)}."
                        else:
                            msg = f"Lumière {piece} allumée."
                    parler(msg)
                elif action == "ha_prise":
                    piece     = data.get("piece", "bureau").lower().strip()
                    etat      = data.get("etat",  "on")
                    entity_id = PIECES_PRISES.get(piece, f"switch.prise_{piece}")
                    ha_interrupteur(entity_id, etat)
                    msg = f"Prise {piece} {'activée' if etat == 'on' else 'désactivée'}."
                    parler(msg)
                elif action == "ha_temperature":
                    piece     = data.get("piece", "salon").lower().strip()
                    entity_id = PIECES_CAPTEURS.get(piece)
                    if entity_id:
                        temp = ha_get_etat(entity_id)
                        parler(f"La température dans le {piece} est de {temp} degrés.")
                    else:
                        parler(f"Désolé, je n'ai pas de capteur configuré pour le {piece}.")
                elif action == "ha_humidite":
                    piece     = data.get("piece", "bureau").lower().strip()
                    entity_id = PIECES_HUMIDITE.get(piece)
                    if entity_id:
                        humi = ha_get_etat(entity_id)
                        parler(f"Le taux d'humidité dans le {piece} est de {humi}%.")
                    else:
                        parler(f"Je n'ai pas de capteur d'humidité pour le {piece}.")
                elif action == "ha_batterie":
                    appareil  = data.get("appareil", "").lower()
                    entity_id = APPAREILS_BATTERIE.get(appareil)
                    if entity_id:
                        batt = ha_get_etat(entity_id)
                        if batt == "unknown":
                            parler(f"Je n'arrive pas à récupérer l'état de la batterie pour {appareil}.")
                        else:
                            suff = ""
                            if "telephone" in appareil or "papa" in appareil or "mylane" in appareil:
                                suff = "Ton téléphone est à "
                            elif "julie" in appareil or "maman" in appareil:
                                suff = "Le téléphone de Julie est à "
                            else:
                                suff = f"La batterie de {appareil} est à "
                            parler(f"{suff}{batt}%.")
                    else:
                        parler(f"Je n'ai pas l'appareil {appareil} dans ma liste de batterie.")
                elif action == "ha_thermostat":
                    temp = data.get("temperature", 20)
                    ha_thermostat("climate.thermostat", temp)
                    parler(f"Thermostat réglé à {temp} degrés.")
                elif action == "ha_scene":
                    nom      = data.get("nom", "")
                    scene_id = f"scene.{nom}"
                    ha_scene(scene_id)
                    parler(f"Ambiance {nom} activée.")
                elif action == "dom_sequence":
                    steps = data.get("steps", [])
                    if hasattr(builtins, "send_web_action"):
                        remaining_steps = []
                        for step in steps:
                            action_type = step.get("action_type", "click")
                            text = step.get("text", "")
                            
                            # Si c'est une ouverture d'URL, on le fait localement via le navigateur par défaut
                            if action_type == "open_url" and text:
                                import webbrowser
                                webbrowser.open(text, new=2)
                                await asyncio.sleep(5.0)  # Laisser le temps au navigateur de charger le site
                                continue
                                
                            remaining_steps.append(step)
                            
                        # Envoyer toutes les étapes DOM restantes en un seul bloc à l'extension
                        if remaining_steps:
                            payload = {"type": "dom_action", "action": "dom_sequence", "steps": remaining_steps}
                            _safe_ws_send(json.dumps(payload))
                elif action == "ha_alarme":
                    etat = data.get("etat", "on")
                    if etat == "on":
                        ha_appeler_service("alarm_control_panel", "alarm_arm_away", "alarm_control_panel.home_base_2")
                        parler("Alarme activée.")
                    else:
                        ha_appeler_service("alarm_control_panel", "alarm_disarm", "alarm_control_panel.home_base_2")
                        parler("Alarme désactivée.")
                elif action == "ha_verrou":
                    entity_id = data.get("entity_id", "lock.porte_maison")
                    etat = data.get("etat", "lock")
                    ha_verrou(entity_id, etat)
                    msg = "Porte verrouillée, mylane." if etat == "lock" else "Porte déverrouillée, mylane."
                    parler(msg)
                elif action == "ha_simulation":
                    etat = data.get("etat", "on")
                    ha_interrupteur("switch.simulation", etat)
                    msg = "Simulation de présence activée." if etat == "on" else "Simulation de présence désactivée."
                    parler(msg)
                elif action == "ha_anniversaires":
                    events = ha_get_calendrier("calendar.anniversaires")
                    if not events:
                        parler("Rien de prévu aujourd'hui.")
                    else:
                        noms = [e.get("summary", "Anniversaire sans nom") for e in events]
                        if len(noms) == 1:
                            parler(f"Aujourd'hui, nous fêtons l'anniversaire de {noms[0]}. N'oubliez pas de lui souhaiter !")
                        else:
                            liste = ", ".join(noms[:-1]) + " et " + noms[-1]
                            parler(f"Aujourd'hui, il y a plusieurs anniversaires : {liste}. C'est une journée chargée !")
                elif action == "ha_consommation":
                    entity_id = PIECES_CAPTEURS.get("consommation")
                    puissance = ha_get_etat(entity_id)
                    if puissance == "unknown" or puissance == "inconnu":
                        parler("Je n'arrive pas à lire la consommation électrique pour le moment.")
                    else:
                        parler(f"La consommation actuelle de la maison est de {puissance} Volt-Ampères.")
                elif action == "ha_tiktok":
                    entity_id = PIECES_CAPTEURS.get("tiktok")
                    followers = ha_get_etat(entity_id)
                    parler(f"Tu as actuellement {followers} abonnés sur ton compte TikTok mylane. Félicitations !")
                elif action == "ha_oeufs":
                    entity_id = PIECES_CAPTEURS.get("oeufs")
                    # On récupère l'état (le dernier choix) et le moment de la modif
                    try:
                        r = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HA_HEADERS, timeout=5)
                        data = r.json()
                        last_changed = data.get("last_changed", "")
                        if last_changed:
                            dt = datetime.fromisoformat(last_changed.replace("Z", "+00:00"))
                            phrase = dt.strftime("le %d %B à %Hh%M")
                            parler(f"Le dernier ramassage des œufs a été enregistré {phrase}.")
                        else:
                            parler("Je n'ai pas d'historique pour le ramassage des œufs.")
                    except:
                        parler("Je n'arrive pas à accéder aux informations sur les œufs.")
                elif action == "ha_energie":
                    periode  = data.get("periode", "mois")
                    appareil = data.get("appareil", "")
                    
                    if appareil:
                        appareil_clean = appareil.lower()
                        entite = APPAREILS_ENERGIE.get(appareil_clean)
                        if entite:
                            val = ha_get_etat(entite)
                            if val != "inconnu" and val != "unknown":
                                kwh = float(val)
                                parler(f"La consommation de {appareil} pour ce mois est de {kwh:.1f} kWh.")
                            else:
                                parler(f"Je n'ai pas de données de consommation pour {appareil} pour le moment.")
                        else:
                            parler(f"Je n'ai pas d'appareil nommé {appareil} dans mon suivi énergétique.")
                    elif periode == "hier":
                        total_kwh = 0
                        total_cost = 0
                        try:
                            for i in range(1, 7):
                                e_id = f"sensor.lixee_zlinky_tic_zlinky_p{i}_daily"
                                val = ha_get_etat(e_id, attribut="last_period")
                                if val != "inconnu" and val != "unknown":
                                    k = float(val)
                                    total_kwh += k
                                    total_cost += k * HA_TARIFS.get(f"p{i}", 0.16)
                            parler(f"Hier, la maison a consommé {total_kwh:.1f} kWh, pour un coût estimé à {total_cost:.2f} euros.")
                        except:
                            parler("J'ai eu un problème pour calculer la consommation d'hier.")
                    else: # mois
                        total_kwh = 0
                        total_cost = 0
                        try:
                            for i in range(1, 7):
                                e_id = f"sensor.lixee_zlinky_tic_zlinky_p{i}_mensuel"
                                val = ha_get_etat(e_id)
                                if val != "inconnu" and val != "unknown":
                                    k = float(val)
                                    total_kwh += k
                                    total_cost += k * HA_TARIFS.get(f"p{i}", 0.16)
                            parler(f"Ce mois-ci, la consommation totale est de {total_kwh:.1f} kWh, pour un montant de {total_cost:.2f} euros.")
                        except:
                            parler("Je n'ai pas pu calculer la consommation mensuelle.")
                elif action == "ha_aspirateur":
                    commande = data.get("commande", "start")
                    if commande == "start":
                        ha_appeler_service("vacuum", "start", "vacuum.bob")
                        parler("C'est parti, Bob lance le nettoyage.")
                    elif commande == "stop":
                        ha_appeler_service("vacuum", "stop", "vacuum.bob")
                        parler("J'ai arrêté l'aspirateur.")
                    elif commande == "pause":
                        ha_appeler_service("vacuum", "pause", "vacuum.bob")
                        parler("Bob est en pause.")
                    elif commande == "base":
                        ha_appeler_service("vacuum", "return_to_base", "vacuum.bob")
                        parler("Bob retourne à sa base.")
                elif action == "homepod_action":
                    cmd   = data.get("commande", "play")
                    val   = data.get("valeur")
                    ok, res = await homepod_controller.send_command(cmd, val)
                    if ok:
                        if cmd == "volume":
                            parler(f"Volume du HomePod réglé à {val}%.")
                        else:
                            parler(f"Commande {cmd} exécutée sur le HomePod.")
                elif action == "open_drive":
                    result = ouvrir_google_drive()
                    parler(result)
                elif action == "search_drive":
                    query = data.get("query") or None
                    if query:
                        parler(f"Je recherche les fichiers contenant '{query}' sur votre Google Drive...")
                    else:
                        parler("Je recherche vos fichiers récents sur votre Google Drive...")
                    result = rechercher_google_drive(nom_fichier=query)
                    parler(result)
                elif action == "create_doc":
                    titre   = data.get("title",   "Document JARVIS")
                    contenu = data.get("content", "")
                    result  = creer_google_doc(titre, contenu)
                    parler(result)
                elif action == "write_doc":
                    contenu = data.get("content", "")
                    result  = modifier_google_doc(contenu)
                    parler(result)
                elif action == "create_sheet":
                    titre  = data.get("title", "Feuille JARVIS")
                    result = creer_google_sheet(titre)
                    parler(result)
                elif action == "read_emails":
                    result = lire_emails()
                    if "Aucun nouvel email" in result:
                        parler("Vous n'avez aucun nouvel email non lu dans votre boîte principale, mylane.")
                    else:
                        parler(f"Voici vos derniers emails non lus, mylane. {result}")
                elif action == "read_calendar":
                    result = lister_evenements_calendar()
                    parler(f"Voici vos prochains evenements mylane. {result}")
                elif action == "create_task":
                    titre = data.get("title") or data.get("titre") or ""
                    notes = data.get("notes") or ""
                    result = creer_google_task(titre, notes)
                    parler(result)
                elif action == "list_tasks":
                    result = lister_google_tasks()
                    parler(f"Voici vos tâches à faire dans Google Tasks, mylane. {result}")
                elif action == "complete_task":
                    titre = data.get("title") or data.get("titre") or ""
                    result = complete_google_task(titre)
                    parler(result)
                elif action == "delete_task":
                    titre = data.get("title") or data.get("titre") or ""
                    result = delete_google_task(titre)
                    parler(result)
                elif action == "send_email":
                    destinataire = data.get("to") or data.get("destinataire") or ""
                    sujet = data.get("subject") or data.get("sujet") or "Message de JARVIS"
                    corps = data.get("body") or data.get("corps") or ""
                    result = envoyer_email(destinataire, sujet, corps)
                    parler(result)
                elif action == "reply_email":
                    corps = data.get("body") or data.get("corps") or ""
                    msg_id = data.get("original_msg_id") or None
                    result = repondre_email(corps, msg_id)
                    parler(result)
                elif action == "read_full_email":
                    msg_id = data.get("msg_id") or None
                    result = lire_detail_email(msg_id)
                    parler(f"Voici le contenu de l'e-mail : {result}")
                elif action == "archive_email":
                    msg_id = data.get("msg_id") or None
                    result = archiver_email(msg_id)
                    parler(result)
                elif action == "delete_email":
                    msg_id = data.get("msg_id") or None
                    result = supprimer_email(msg_id)
                    parler(result)
                elif action == "create_event":
                    summary = data.get("summary") or data.get("titre") or "Événement"
                    start_time = data.get("start") or data.get("debut") or ""
                    end_time = data.get("end") or data.get("fin") or ""
                    description = data.get("description") or None
                    result = creer_evenement_calendar(summary, start_time, end_time, description)
                    parler(result)
                elif action == "update_event":
                    old_title = data.get("old_title") or data.get("ancien_titre") or ""
                    new_title = data.get("new_title") or data.get("nouveau_titre") or None
                    new_start = data.get("new_start") or data.get("nouvelle_heure") or None
                    new_end = data.get("new_end") or data.get("fin_heure") or None
                    result = modifier_evenement_calendar(old_title, new_title, new_start, new_end)
                    parler(result)
                elif action == "delete_event":
                    title = data.get("title") or data.get("titre") or ""
                    result = supprimer_evenement_calendar(title)
                    parler(result)
                elif action == "append_sheet":
                    valeurs = data.get("values") or data.get("valeurs") or []
                    sheet_id = data.get("spreadsheet_id") or None
                    onglet = data.get("onglet") or "Feuille 1"
                    result = ajouter_ligne_sheet(valeurs, sheet_id, onglet)
                    parler(result)
                elif action == "read_sheet":
                    cell_range = data.get("range") or data.get("plage") or "A1:Z10"
                    sheet_id = data.get("spreadsheet_id") or None
                    result = lire_donnees_sheet(cell_range, sheet_id)
                    parler(f"Voici les données lues de la feuille : {result}")
                elif action == "read_doc":
                    doc_id = data.get("doc_id") or None
                    result = lire_contenu_doc(doc_id)
                    parler(f"Voici le contenu du document : {result}")
                elif action == "upload_file":
                    local_path = data.get("local_path") or data.get("chemin") or ""
                    folder_id = data.get("folder_id") or data.get("dossier_id") or None
                    result = charger_fichier_drive(local_path, folder_id)
                    parler(result)
                elif action == "share_file":
                    email = data.get("email") or data.get("destinataire") or ""
                    role = data.get("role") or "reader"
                    file_id = data.get("file_id") or None
                    result = partager_fichier_drive(email, role, file_id)
                    parler(result)
                elif action == "create_folder":
                    folder_name = data.get("folder_name") or data.get("nom_dossier") or "Nouveau Dossier"
                    parent_folder_id = data.get("parent_folder_id") or data.get("dossier_parent_id") or None
                    result = creer_dossier_drive(folder_name, parent_folder_id)
                    parler(result)
                elif action == "meteo":
                    ville = data.get("ville") or None
                    parler("Je consulte la meteo, un instant mylane.")
                    result = get_meteo_actuelle(ville)
                    parler(result)
                elif action == "alerte_meteo":
                    ville = data.get("ville") or None
                    result = get_alertes_meteo(ville)
                    parler(result)
                elif action == "recherche_web":
                    query = data.get("query", "")
                    parler(f"Je lance une recherche sur internet pour {query}.")
                    result = recherche_web_serpapi(query)
                    parler(result)
                elif action == "recherche_approfondie":
                    query = data.get("query", "")
                    parler(f"Je lance une recherche approfondie sur {query}, mylane. Cela peut prendre quelques secondes pendant que j'analyse les sources.")
                    # Appel de l'agent autonome
                    research_data = await browser_agent.search_and_browse(query)
                    if not research_data or "error" in research_data[0]:
                        parler("Je suis désolé mylane, mais je n'ai pas pu accéder aux sites web pour le moment.")
                    else:
                        # On prépare un prompt pour que l'IA synthétise les résultats
                        context = "\n\n".join([f"Source: {d['url']}\nContenu: {d['content']}" for d in research_data])
                        prompt_synthese = (
                            f"Voici les résultats de ma recherche approfondie sur '{query}' :\n\n"
                            f"{context}\n\n"
                            f"En tant que JARVIS, fais une synthèse élégante, précise et complète de ces informations pour mylane."
                        )
                        synthese = await demander_ia(prompt_synthese, update_hist=False, skip_local=True)
                        if synthese:
                            print("\n[BROWSER] --- SOURCES CONSULTÉES ---")
                            for d in research_data:
                                print(f" > {d['url']}")
                            print("[BROWSER] ---------------------------\n")
                            parler(synthese)

                elif action == "web_agent_task":
                    task_desc = data.get("task", "")
                    if not task_desc:
                        parler("Désolé mylane, je n'ai pas compris la tâche à effectuer.")
                    else:
                        result = await run_visual_agent(task_desc)
                        parler(result)

                elif action == "fermer_navigateur_agent":
                    result = await stop_visual_agent()
                    parler(result)

                elif action == "sport_resultats":
                    equipe = data.get("equipe") or None
                    ligue  = data.get("ligue")  or None
                    print(f"[SPORT] Action sport_resultats pour {equipe or ligue}")
                    parler(f"Je cherche les informations pour {equipe or ligue}, un instant.")
                    result = get_resultats_football(equipe=equipe, ligue=ligue)
                    if "pas trouvé" in result or "Impossible" in result:
                        print(f"[SPORT] Echec recherche locale. Verification avec Grok...")
                        if grok_client:
                            res_grok = await demander_grok(f"mylane veut savoir : {texte_utilisateur}. Je n'ai pas trouvé l'info dans ma base de données football, peux-tu chercher pour lui ?")
                            if res_grok: result = res_grok
                    parler(result)
                elif action == "sport_classement":
                    ligue  = data.get("ligue", "Ligue 1")
                    parler(f"Je recupere le classement {ligue}.")
                    result = get_classement_football(ligue=ligue)
                    parler(result)
                elif action == "sport_live":
                    question = data.get("question", "derniers resultats sportifs 2026")
                    parler("Je recherche les derniers resultats en direct, un instant mylane.")
                    result = get_resultats_sport_gemini(question)
                    parler(result)
                elif action == "voir_ecran":
                    inst = data.get("instruction", "")
                    res = await jarvis_vision_cliquer(inst)
                    parler(res)
                elif action == "whatsapp_appel":
                    contact = data.get("contact")
                    if contact:
                        await action_whatsapp_appel(contact)
                        parler(f"Appel WhatsApp vers {contact} lancé.")
                    else:
                        parler("Désolé mylane, je n'ai pas trouvé le nom du contact à appeler.")
                elif action == "vision_ecrire":
                    inst = data.get("instruction", "")
                    txt  = data.get("texte", "")
                    res  = await jarvis_vision_ecrire(inst, txt)
                    parler(res)
                elif action == "vision_chercher_sur_site":
                    txt = data.get("texte", "")
                    parler(f"Je cherche la barre de recherche sur ce site, mylane.")
                    res = await jarvis_vision_rechercher_sur_site(txt)
                    parler(res)
                elif action == "lance_camera":
                    res = await jarvis_vision_camera(texte_utilisateur)
                    parler(res)
                elif action == "vision_navigateur":
                    res = await jarvis_vision_navigateur(texte_utilisateur)
                    parler(res)
                elif action == "analyse_live":
                    question = data.get("question", "Analyse mon écran et aide-moi.")
                    parler("Je jette un œil à votre écran, un instant mylane.")
                    res = await jarvis_vision_analyse_live(question)
                    parler(res)

                elif action == "dictee":
                    texte = data.get("texte", "")
                    if texte:
                        import pyautogui
                        import pyperclip
                        pyperclip.copy(texte)
                        time.sleep(0.1)
                        pyautogui.hotkey('ctrl', 'v')
                        parler("C'est tapé, mylane.")
                
                # --- ACTIONS ALARMES ---
                elif action == "alarme_set":
                    heure = data.get("heure", "")
                    label = data.get("label", "Alarme")
                    ok, msg = ajouter_alarme(heure, label)
                    parler(msg)
                elif action == "alarme_list":
                    msg = lister_alarmes()
                    # Si l'intro de l'IA annonce déjà les alarmes, on retire le préfixe redondant
                    intro_lower = reponse_propre.lower()
                    if "voici vos alarmes" in intro_lower or "voici tes alarmes" in intro_lower:
                        if msg.startswith("Voici vos alarmes :"):
                            msg = msg[len("Voici vos alarmes :"):].strip()
                    parler(msg)
                elif action == "alarme_cancel":
                    heure = data.get("heure", "")
                    label = data.get("label", "")
                    ok, msg = annuler_alarme(heure, label)
                    parler(msg)
                elif action in ("spotify_ouvrir", "deezer_ouvrir"):
                    parler("J'ouvre Deezer, mylane.")
                    res = await deezer_ouvrir()
                    parler(res)
                elif action in ("spotify_rechercher", "deezer_rechercher"):
                    recherche = data.get("recherche", "")
                    parler(f"Je recherche '{recherche}' sur Deezer, mylane.")
                    res = await deezer_rechercher(recherche)
                    parler(res)
                elif action in ("spotify_lecture_pause", "deezer_lecture_pause"):
                    res = await deezer_lecture_pause()
                    parler(res)
                elif action in ("spotify_stop", "deezer_stop"):
                    res = await deezer_stop()
                    parler(res)
                elif action in ("spotify_suivant", "deezer_suivant"):
                    res = await deezer_suivant()
                    parler(res)
                elif action in ("spotify_precedent", "deezer_precedent"):
                    res = await deezer_precedent()
                    parler(res)
                elif action in ("spotify_volume", "deezer_volume"):
                    direction = data.get("direction", "monter")
                    paliers   = data.get("paliers", 4)
                    res = await deezer_volume(direction, paliers)
                    parler(res)
                else:
                    # Envoi par défaut au frontend pour les actions personnalisées/inconnues
                    if "action" in data or "type" in data:
                        _safe_ws_send(block)

            except Exception as e:
                print(f"[ACTION ERROR] Block failed: {block} | Error: {e}")
                if grok_client:
                    print("[JARVIS] Bascule sur Grok suite a une erreur d'action...")
                    res_grok = await demander_grok(f"mylane m'a demandé : {texte_utilisateur}. J'ai tenté de lancer une action mais j'ai eu une erreur technique ({e}). Peux-tu prendre le relais et lui répondre élégamment ?")
                    if res_grok: parler(res_grok)
                continue

        _skip_pc_audio = False
        return


def nettoyer_commande(texte):
    t = texte.lower().strip()
    for variante in ["jarvis,", "jarvis"]:
        if t.startswith(variante):
            t = t[len(variante):].strip()
    return t

WAKE_WORD       = "jarvis"
SESSION_TIMEOUT = 20.0
STOP_PARLER      = False
is_listening     = False
is_speaking      = False
jarvis_actif     = False
dernier_message  = 0
interface_deja_connectee = False


# ══════════════════════════════════════════════════════════════
#  TRANSCRIPTION AUDIO — Groq Whisper + Fallback Google STT
# ══════════════════════════════════════════════════════════════

import tempfile
import wave

def transcribe_audio_groq(raw_audio_bytes, sample_rate=16000, recognizer=None):
    """
    Transcrit un segment audio brut (PCM 16-bit mono) via Groq Whisper.
    Fallback automatique sur Google STT si Groq échoue.
    
    Args:
        raw_audio_bytes: bytes PCM bruts (int16, mono)
        sample_rate: fréquence d'échantillonnage (défaut 16000)
        recognizer: instance sr.Recognizer pour le fallback Google
    
    Returns:
        str: texte transcrit en minuscules, ou None si échec total
    """
    # --- TENTATIVE 1 : Groq Whisper (ultra-rapide, ~150ms) ---
    if groq_client:
        tmp_path = None
        try:
            t0 = time.time()
            # Écriture du WAV temporaire
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(tmp_fd)
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(sample_rate)
                wf.writeframes(raw_audio_bytes)
            
            # Appel API Groq Whisper
            with open(tmp_path, "rb") as audio_file:
                transcription = groq_client.audio.transcriptions.create(
                    file=("audio.wav", audio_file.read()),
                    model="whisper-large-v3",
                    language="fr",
                    response_format="text",
                )
            
            elapsed = time.time() - t0
            texte = transcription.strip().lower() if isinstance(transcription, str) else str(transcription).strip().lower()
            
            # Filtrer les hallucinations Whisper courantes sur le silence/bruit
            texte_clean = texte.rstrip('.!? ')
            hallucinations = {
                "merci", "merci beaucoup", "merci à tous", "je vous remercie",
                "bonjour", "you", "thank you", "subtitles", "sous-titres",
                "sous-titres par amara.org", "sous-titres réalisés par la communauté d'amara.org",
                "subtitles by amara.org",
                "sous-titrage société radio-canada", "sous-titrage société radio canada",
                "sous-titres société radio-canada", "sous-titres société radio canada",
                "sous-titres par la société radio-canada", "société radio-canada", "radio-canada",
                "sous-titrage st' 501", "sous-titrage st 501", "sous-titres st' 501", "sous-titres st 501",
                "sous-titrage", "sous-titres par"
            }
            if texte_clean in hallucinations:
                if jarvis_actif or (WAKE_WORD in texte):
                    print(f"[STT] Groq Whisper : Hallucination potentielle détectée ('{texte}'), repli sur Google.")
                return None

            if texte and len(texte) > 1:
                if jarvis_actif or (WAKE_WORD in texte):
                    print(f"[STT] Groq Whisper OK ({elapsed:.2f}s) : {texte}")
                return texte
            else:
                if jarvis_actif:
                    print(f"[STT] Groq Whisper : réponse vide, fallback Google.")
        except Exception as e:
            if jarvis_actif:
                print(f"[STT] Groq Whisper erreur : {e} — fallback Google.")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try: os.remove(tmp_path)
                except: pass
    
    # --- TENTATIVE 2 : Google STT (fallback fiable) ---
    if recognizer:
        try:
            audio_data = sr.AudioData(raw_audio_bytes, sample_rate, 2)
            texte = recognizer.recognize_google(audio_data, language="fr-FR").lower().strip()
            if texte:
                if jarvis_actif or (WAKE_WORD in texte):
                    print(f"[STT] Google STT (fallback) : {texte}")
                return texte
        except sr.UnknownValueError:
            pass  # Silence ou parole non reconnue
        except Exception as e:
            print(f"[STT] Google STT erreur : {e}")
    
    return None


def ecouter():
    global is_listening, jarvis_actif, dernier_message, STOP_PARLER, is_speaking, dernier_parle_time, MIC_MUTED, MIC_NEED_RELOAD

    r = sr.Recognizer()
    mic_index = detecter_microphone()
    
    # Paramètres VAD
    RATE = 16000
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    
    # Seuil d'énergie (ajustable dynamiquement)
    ENERGY_THRESHOLD = 800 
    SILENCE_LIMIT = 0.7 if VAD_MODEL is not None else 1.0  # s de silence avant de couper
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                        input=True, frames_per_buffer=CHUNK, input_device_index=mic_index)
    except Exception as e:
        print(f"[MIC] Erreur ouverture flux streaming : {e}")
        return

    print("[JARVIS] Streaming VAD actif. En attente de parole...")

    audio_buffer = []
    is_recording = False
    silence_start = None
    
    # --- Transcription intérimaire en temps réel ---
    INTERIM_INTERVAL = 1.2  # secondes entre chaque transcription partielle
    last_interim_time = 0.0
    _interim_lock = threading.Lock()
    
    def _envoyer_interim(audio_chunks, rate):
        """Thread non-bloquant : transcrit le buffer partiel et envoie au HUD."""
        try:
            raw = b"".join(audio_chunks)
            if len(raw) < rate:  # Moins de 0.5s d'audio (16-bit mono = 2 bytes/sample)
                return
            # Transcription partielle via Groq uniquement (pas de fallback pour l'interim)
            if not groq_client:
                return
            tmp_path = None
            try:
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
                os.close(tmp_fd)
                with wave.open(tmp_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(rate)
                    wf.writeframes(raw)
                
                with open(tmp_path, "rb") as af:
                    result = groq_client.audio.transcriptions.create(
                        file=("interim.wav", af.read()),
                        model="whisper-large-v3",
                        language="fr",
                        response_format="text",
                    )
                texte = result.strip() if isinstance(result, str) else str(result).strip()
                if texte and len(texte) > 1:
                    if jarvis_actif or (WAKE_WORD in texte.lower()):
                        _safe_ws_send(json.dumps({"action": "interim_speech", "text": texte}))
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try: os.remove(tmp_path)
                    except: pass
        except Exception as e:
            pass  # Silencieux — l'interim est cosmétique, pas critique
    
    while True:
        try:
            if MIC_NEED_RELOAD:
                print("[MIC] Rechargement du micro demande...")
                try:
                    stream.stop_stream()
                    stream.close()
                except: pass
                mic_index = detecter_microphone()
                try:
                    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                                    input=True, frames_per_buffer=CHUNK, input_device_index=mic_index)
                    print(f"[MIC] Stream redemarre avec index {mic_index}.")
                except Exception as e:
                    print(f"[MIC] Erreur redemarrage : {e}")
                MIC_NEED_RELOAD = False
                continue

            if MIC_MUTED:
                time.sleep(0.1)
                continue

            # Synchronisation du dernier message depuis les modules/plugins
            if hasattr(builtins, "dernier_message"):
                dernier_message = builtins.dernier_message
                delattr(builtins, "dernier_message")

            # 1. Gestion du timeout de session
            if jarvis_actif and (time.time() - dernier_message > SESSION_TIMEOUT):
                print(f"[JARVIS] Timeout session ({SESSION_TIMEOUT}s). Retour en veille.")
                jarvis_actif = False
                _safe_ws_send(json.dumps({"action": "jarvis_text", "text": ""}))
                try:
                    asyncio.run(send_web_state("idle"))
                except: pass

            # 2. Lecture du flux audio
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_chunk_int16 = np.frombuffer(data, dtype=np.int16)
            except Exception:
                continue

            # 3. BARGE-IN AUTOMATIQUE DÉSACTIVÉ (À la demande de l'utilisateur)
            # JARVIS ne s'arrête plus au bruit ambiant, seulement sur commande vocale "Stop/Silence"
            else:
                ecouter._noise_count = 0

            # 4. LOGIQUE VAD (Capture de la phrase)
            is_speech = False
            if VAD_MODEL is not None:
                try:
                    speech_prob = VAD_MODEL(audio_chunk_int16, RATE)
                    is_speech = speech_prob > 0.45
                except Exception as ev:
                    energy = np.sqrt(np.mean(audio_chunk_int16.astype(np.float64)**2))
                    is_speech = energy > ENERGY_THRESHOLD
            else:
                energy = np.sqrt(np.mean(audio_chunk_int16.astype(np.float64)**2))
                is_speech = energy > ENERGY_THRESHOLD

            if is_speech:
                if not is_recording:
                    if not get_is_speaking():
                        try: asyncio.run(send_web_state("listening"))
                        except: pass
                    is_recording = True
                    audio_buffer = [data]
                    last_interim_time = time.time()  # Reset timer interim
                else:
                    audio_buffer.append(data)
                    # --- TRANSCRIPTION INTÉRIMAIRE EN TEMPS RÉEL ---
                    now = time.time()
                    if now - last_interim_time >= INTERIM_INTERVAL and groq_client:
                        last_interim_time = now
                        # Copie du buffer pour le thread (évite les race conditions)
                        buffer_copy = list(audio_buffer)
                        threading.Thread(
                            target=_envoyer_interim,
                            args=(buffer_copy, RATE),
                            daemon=True
                        ).start()
                silence_start = None
            elif is_recording:
                audio_buffer.append(data)
                if silence_start is None:
                    silence_start = time.time()
                
                if time.time() - silence_start > SILENCE_LIMIT:
                    is_recording = False
                    if VAD_MODEL is not None:
                        VAD_MODEL.reset_states()
                    try: asyncio.run(send_web_state("idle"))
                    except: pass
                    
                    raw_audio = b"".join(audio_buffer)
                    
                    try:
                        # Transcription Groq Whisper avec fallback Google STT
                        texte = transcribe_audio_groq(raw_audio, RATE, r)
                        
                        if time.time() - get_dernier_parle_time() < 0.8:
                            audio_buffer = []
                            continue

                        if texte:
                            is_relevant = (WAKE_WORD in texte.lower()) or jarvis_actif
                            if not is_relevant:
                                _safe_ws_send(json.dumps({"action": "jarvis_text", "text": ""}))
                                audio_buffer = []
                                continue
                                
                            print(f"[VAD ENTENDU] {texte}")
                            dernier_message = time.time()
                            
                            # --- BIOMÉTRIE : IDENTIFIER LE LOCUTEUR ---
                            global ACTIVE_SPEAKER, SPEAKER_ANNOUNCED
                            if VOICE_BIOMETRICS:
                                try:
                                    name, score = VOICE_BIOMETRICS.identify_speaker(raw_audio, RATE)
                                    voiceprints = VOICE_BIOMETRICS.load_voiceprints()
                                    if not voiceprints:
                                        ACTIVE_SPEAKER = "mylane"
                                        builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
                                        print(f"🎙  [SPEAKER] Aucun profil enregistré. Par défaut : {ACTIVE_SPEAKER}")
                                    else:
                                        ACTIVE_SPEAKER = name
                                        builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
                                        if name != "guest":
                                            print(f"🎙  [SPEAKER] Utilisateur authentifié : {name} (Similarité: {score:.2f})")
                                        else:
                                            print(f"🎙  [SPEAKER] Utilisateur inconnu (max Similarité: {score:.2f}). Mode invité activé.")
                                            
                                    # Annonce vocale unique si changement de locuteur dans la session
                                    if SPEAKER_ANNOUNCED != ACTIVE_SPEAKER:
                                        SPEAKER_ANNOUNCED = ACTIVE_SPEAKER
                                        if ACTIVE_SPEAKER == "guest":
                                            parler("Bonjour, votre voix n'a pas été reconnue. Connexion en mode invité restreint.")
                                        else:
                                            parler(f"Bonjour {ACTIVE_SPEAKER.capitalize()}, j'ai reconnu votre voix. Connexion sécurisée établie.")
                                except Exception as eb:
                                    print(f"❌  [SPEAKER] Erreur lors de l'identification : {eb}")
                            
                            if get_is_speaking() and any(w in texte for w in ["tais-toi", "silence", "stop", "chut", "arrête-toi", "arrête toi", "stoppe"]):
                                STOP_PARLER = True
                                set_stop_parler(True)
                                speech.vider_files()
                                audio_buffer = []
                                print("[JARVIS] Interruption forcée : File de parole vidée.")
                                continue
                            
                            if WAKE_WORD in texte or jarvis_actif:
                                if WAKE_WORD in texte: jarvis_actif = True
                                commande = nettoyer_commande(texte)
                                
                                if commande:
                                    STOP_PARLER = False
                                    set_stop_parler(False)


                                    # --- TEST CARTES CONTEXTUELLES ---
                                    if "test carte" in commande or "affiche carte" in commande:
                                        loop = asyncio.new_event_loop()
                                        loop.run_until_complete(envoyer_carte_contextuelle(
                                            "Test Protocole", 
                                            "Ceci est une carte de test générée par le nouveau système contextuel. Tous les capteurs sont opérationnels.",
                                            type_carte="info",
                                            icon="◈"
                                        ))
                                        parler("Carte de test affichée sur le HUD, mylane.")
                                        loop.close()
                                        audio_buffer = []
                                        continue
                                    
                                    # --- ENREGISTREMENT VOCAL / BIOMÉTRIE ---
                                    if "enregistre la voix de" in commande or "apprends la voix de" in commande or "enregistre ma voix" in commande:
                                        prenom = "mylane"
                                        if "enregistre la voix de" in commande:
                                            prenom = commande.split("enregistre la voix de")[-1].strip()
                                        elif "apprends la voix de" in commande:
                                            prenom = commande.split("apprends la voix de")[-1].strip()
                                        
                                        prenom = re.sub(r'[^a-zA-Z0-9_-]', '', prenom).lower()
                                        if not prenom:
                                            prenom = "mylane"
                                            
                                        parler(f"Très bien. Je vais enregistrer votre voix pour le profil {prenom.capitalize()}. Préparez-vous à parler pendant 5 secondes après le signal...")
                                        time.sleep(4.5)
                                        parler("C'est à vous, parlez maintenant.")
                                        
                                        enroll_buffer = []
                                        try:
                                            if stream.is_active():
                                                while stream.get_read_available() > 0:
                                                    stream.read(CHUNK, exception_on_overflow=False)
                                        except:
                                            pass
                                            
                                        t_end = time.time() + 5.0
                                        while time.time() < t_end:
                                            try:
                                                enroll_data = stream.read(CHUNK, exception_on_overflow=False)
                                                enroll_buffer.append(enroll_data)
                                            except:
                                                pass
                                                
                                        parler("Merci, enregistrement terminé. Analyse en cours...")
                                        raw_enroll_audio = b"".join(enroll_buffer)
                                        
                                        if VOICE_BIOMETRICS:
                                            try:
                                                emb = VOICE_BIOMETRICS.get_embedding(raw_enroll_audio, RATE)
                                                if emb is not None:
                                                    VOICE_BIOMETRICS.save_voiceprint(prenom, emb)
                                                    print(f"✔  [BIOMETRICS] Empreinte vocale enregistrée pour : {prenom}")
                                                    parler(f"C'est parfait {prenom.capitalize()}, votre voix a été enregistrée avec succès. Vous êtes désormais reconnu.")
                                                    ACTIVE_SPEAKER = prenom
                                                    builtins.ACTIVE_SPEAKER = ACTIVE_SPEAKER
                                                else:
                                                    parler("Désolé, je n'ai pas réussi à extraire une empreinte vocale claire. Parlez bien fort et distinctement.")
                                            except Exception as eb:
                                                print(f"❌  [BIOMETRICS] Erreur d'analyse : {eb}")
                                                parler("Une erreur est survenue lors de l'analyse de votre voix.")
                                        else:
                                            parler("Le système de biométrie vocale n'est pas initialisé.")
                                            
                                        audio_buffer = []
                                        continue

                                    action_pc = executer_action_pc(commande)
                                    if action_pc:
                                        parler(action_pc)
                                    else:
                                        loop = asyncio.new_event_loop()
                                        loop.run_until_complete(traiter_reponse_ia(commande, from_voice=True))
                                        loop.close()
                                elif WAKE_WORD in texte:
                                    parler("Oui mylane, je vous écoute.")
                        else:
                            _safe_ws_send(json.dumps({"action": "jarvis_text", "text": ""}))
                                    
                    except Exception as e:
                        print(f"[VAD] Erreur reconnaissance : {e}")
                    
                    audio_buffer = []

        except Exception as e:
            print(f"[VAD] Erreur boucle principale : {e}")
            time.sleep(1)

    stream.stop_stream()
    stream.close()
    p.terminate()


# ══════════════════════════════════════════════════════════════
#  DÉTECTION MICROPHONE — Énumération + Fallback automatique
# ══════════════════════════════════════════════════════════════

_JARVIS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_config.json")

def _charger_config() -> dict:
    """Charge jarvis_config.json ou retourne un dict vide si absent/corrompu."""
    try:
        if os.path.exists(_JARVIS_CONFIG_PATH):
            import json
            with open(_JARVIS_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _sauvegarder_config(data: dict) -> None:
    """Sauvegarde les données dans jarvis_config.json."""
    try:
        import json
        cfg = _charger_config()
        cfg.update(data)
        with open(_JARVIS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[MIC] Impossible de sauvegarder la config : {e}")

def detecter_microphone() -> int | None:
    """
    Détecte le meilleur microphone disponible.

    Stratégie :
      1. Essaie l'index mémorisé dans jarvis_config.json
      2. Essaie le micro par défaut du système (index None)
      3. Parcourt tous les périphériques d'entrée disponibles
      4. Sauvegarde l'index retenu pour le prochain lancement

    Retourne l'index (int) du micro retenu, ou None si aucun trouvé
    (dans ce cas sr.Microphone() utilisera le défaut OS).
    """
    import json

    # ── Lister tous les périphériques PyAudio ────────────────
    if pyaudio:
        try:
            p = pyaudio.PyAudio()
            nb = p.get_device_count()
            inputs = []
            raw_devices = []
            for i in range(nb):
                try:
                    info = p.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        nom = info.get("name", f"Périphérique {i}")
                        inputs.append((i, nom))
                        
                        # Normaliser et filtrer les périphériques système/virtuels indésirables
                        nom_normalise = nom.lower().strip()
                        exclus = ["mappeur de sons", "capture audio principal", "mixage", "stereo mix", "ivcam", "entrée ligne", "line input", "realtek hd audio mic input"]
                        if any(x in nom_normalise for x in exclus):
                            continue
                            
                        # Nettoyage cosmétique du nom pour fusionner les doublons physiques
                        nom_propre = re.sub(r'\d+-\s*', '', nom) # Retirer les préfixes comme "3- " ou "6- "
                        nom_propre = re.sub(r'sur casque', '', nom_propre, flags=re.IGNORECASE)
                        nom_propre = nom_propre.replace("Headset Microphone", "Microphone")
                        # Supprimer les parenthèses vides ou ne contenant que des espaces
                        nom_propre = re.sub(r'\(\s*\)', '', nom_propre)
                        nom_propre = re.sub(r'\s+', ' ', nom_propre).strip() # Normaliser les espaces doubles
                        
                        # Ignorer si le nom est trop générique ou vide
                        if nom_propre.lower() in ["microphone", ""]:
                            continue
                            
                        raw_devices.append({"index": i, "clean_name": nom_propre})
                except Exception:
                    pass
            p.terminate()

            # Déduplication intelligente par longueur décroissante (priorité aux noms complets non tronqués)
            raw_devices.sort(key=lambda d: len(d["clean_name"]), reverse=True)
            seen_clean_names = set()
            filtered_devices = []
            
            for dev in raw_devices:
                name_lower = dev["clean_name"].lower()
                # Ignorer si c'est un préfixe ou une sous-chaîne d'un nom plus complet déjà enregistré
                is_truncated_duplicate = any(name_lower in seen or seen.startswith(name_lower) for seen in seen_clean_names)
                if not is_truncated_duplicate:
                    seen_clean_names.add(name_lower)
                    filtered_devices.append(dev)
            
            # Réordonner par index croissant pour l'affichage console final
            filtered_devices.sort(key=lambda d: d["index"])
            
            print("[MIC] Périphériques audio détectés (filtrés et nettoyés) :")
            for dev in filtered_devices:
                print(f"      [{dev['index']}] {dev['clean_name']}")

            if not inputs:
                print("[MIC] ⚠ Aucun périphérique d'entrée détecté par PyAudio.")
        except Exception as e:
            print(f"[MIC] Impossible de lister les périphériques : {e}")
            inputs = []
    else:
        inputs = []
        print("[MIC] PyAudio absent — mode fallback speech_recognition uniquement.")

    # ── Récupérer l'index mémorisé ───────────────────────────
    cfg = _charger_config()
    index_memo = cfg.get("mic_device_index", None)

    # ── Fonction de test d'un index ──────────────────────────
    def _tester_index(idx):
        """Retourne True si sr.Microphone(device_index=idx) s'ouvre correctement."""
        try:
            kwargs = {} if idx is None else {"device_index": idx}
            mic_test = sr.Microphone(**kwargs)
            r_test = sr.Recognizer()
            with mic_test as src:
                r_test.adjust_for_ambient_noise(src, duration=0.3)
            return True
        except Exception as e:
            label = "défaut" if idx is None else str(idx)
            print(f"[MIC]   Index {label} → KO ({e})")
            return False

    # ── Priorité 1 : index mémorisé ──────────────────────────
    if index_memo is not None:
        nom_memo = next((n for i, n in inputs if i == index_memo), f"Index {index_memo}")
        print(f"[MIC] Test du micro mémorisé : [{index_memo}] {nom_memo}")
        if _tester_index(index_memo):
            print(f"[MIC] [OK] Micro retenu (mémorisé) : [{index_memo}] {nom_memo}")
            return index_memo
        else:
            print(f"[MIC] Micro mémorisé introuvable, recherche d'un remplaçant…")

    # ── Priorité 2 : micro par défaut OS ─────────────────────
    print("[MIC] Test du micro par défaut système…")
    if _tester_index(None):
        # Identifier son index réel si possible
        idx_reel = None
        if pyaudio:
            try:
                p = pyaudio.PyAudio()
                idx_reel = p.get_default_input_device_info().get("index", None)
                p.terminate()
            except Exception:
                pass
        nom_defaut = next((n for i, n in inputs if i == idx_reel), "Défaut système")
        print(f"[MIC] [OK] Micro retenu (défaut) : [{idx_reel}] {nom_defaut}")
        _sauvegarder_config({"mic_device_index": idx_reel})
        return idx_reel

    # ── Priorité 3 : parcourir tous les périphériques ────────
    print("[MIC] Recherche sur tous les périphériques disponibles…")
    for idx, nom in inputs:
        print(f"[MIC]   Test [{idx}] {nom}…")
        if _tester_index(idx):
            print(f"[MIC] [OK] Micro retenu (fallback) : [{idx}] {nom}")
            _sauvegarder_config({"mic_device_index": idx})
            return idx

    # ── Aucun micro fonctionnel ───────────────────────────────
    print("[MIC] ⚠ Aucun microphone fonctionnel trouvé.")
    print("[MIC]   Vérifiez que votre micro est branché et autorisé dans")
    print("[MIC]   Paramètres Windows → Confidentialité → Microphone.")
    _sauvegarder_config({"mic_device_index": None})
    return None



def monitor_claps():
    if not pyaudio:
        print("[CLAP] PyAudio absent — detection des applaudissements desactivee.")
        return
    try:
        import audioop
        p = pyaudio.PyAudio()
        # On ouvre le flux
        # Utiliser le même micro que la détection vocale
        cfg_clap = _charger_config()
        mic_idx_clap = cfg_clap.get("mic_device_index", None)
        open_kwargs = dict(format=pyaudio.paInt16, channels=1, rate=44100,
                          input=True, frames_per_buffer=1024)
        if mic_idx_clap is not None:
            open_kwargs["input_device_index"] = mic_idx_clap
        stream = p.open(**open_kwargs)
        print("[CLAP] Détection des applaudissements activée (Double clap = réveiller, Simple clap = couper la parole).")
        
        last_clap_time = 0
        
        while True:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                rms  = audioop.rms(data, 2)
                
                # Ignorer uniquement si Jarvis réfléchit pour éviter les surcharges
                if is_thinking:
                    last_clap_time = 0
                    continue

                if rms > CLAP_THRESHOLD:
                    current_time = time.time()
                    diff = current_time - last_clap_time
                    
                    # 1. SIMPLE CLAP : Si Jarvis est en train de parler, on l'interrompt immédiatement
                    if get_is_speaking():
                        global STOP_PARLER
                        STOP_PARLER = True
                        set_stop_parler(True)
                        speech.vider_files()
                        print("[CLAP] Parole interrompue via simple clap.")
                    
                    # 2. DOUBLE CLAP : Si l'intervalle correspond, on réveille Jarvis
                    if 0.1 < diff < 0.8:
                        global jarvis_actif, dernier_message
                        print(f"\n[CLAP] !!! DOUBLE CLAP DÉTECTÉ !!! Réveil de Jarvis")
                        
                        jarvis_actif = True
                        dernier_message = current_time
                        
                        # Mettre à jour l'interface Web et WebSocket
                        _safe_ws_send(json.dumps({"action": "set_state", "state": "listening"}))
                        _safe_ws_send(json.dumps({"action": "jarvis_text", "text": "Oui mylane, je vous écoute."}))
                        
                        # Dire la phrase d'accueil
                        parler("Oui mylane, je vous écoute.")
                        
                        # Debounce pour éviter la boucle de claps
                        time.sleep(2.0)
                        last_clap_time = 0
                    else:
                        # Premier clap enregistré
                        last_clap_time = current_time
            except Exception as e:
                # Si erreur de lecture (ex: micro débranché), on attend et on continue
                time.sleep(0.5)
                continue

    except Exception as e:
        print(f"[CLAP] Erreur fatale détection claps : {e}")

def verifier_mises_a_jour():
    """Vérifie si une nouvelle version est disponible sur le serveur."""
    global DERNIERE_MAJ_INFO
    try:
        print(f"[UPDATE] Verification des mises a jour...")
        response = requests.get(UPDATE_JSON_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            remote_version = data.get("version", "4.0")
            
            # Comparaison de version
            if remote_version > CURRENT_VERSION:
                print(f"[UPDATE] NOUVELLE VERSION DETECTEE : {remote_version}")
                DERNIERE_MAJ_INFO = {
                    "type": "update_available",
                    "version": remote_version,
                    "url": data.get("download_url", "https://www.techenclair.fr/pages/jarvis.html"),
                    "changelog": data.get("changelog", "")
                }
            else:
                print(f"[UPDATE] Systeme a jour (v{CURRENT_VERSION})")
                DERNIERE_MAJ_INFO = None
        else:
            print(f"[UPDATE] Serveur injoignable (Status: {response.status_code})")
    except Exception as e:
        print(f"[UPDATE] Erreur lors de la verification : {e}")

def verifier_mises_a_jour_loop():
    """Boucle de vérification périodique (toutes les 4 heures)."""
    while True:
        time.sleep(14400)
        verifier_mises_a_jour()

def start_ia():
    threading.Thread(target=monitor_claps, daemon=True).start()
    
    # Légère attente pour s'assurer du bon ordonnancement avec les messages du thread claps
    time.sleep(0.15)
    nb_conv = len(historique) // 2 if 'historique' in globals() else 0
    print(f"[CONV] {nb_conv} conversations chargées en mémoire")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def start_ws():
        global WS_LOOP
        WS_LOOP = asyncio.get_running_loop()
        print("[WEB] Serveur WebSocket de communication démarré.")
        
        # Lancer le monitoring système en arrière-plan
        asyncio.create_task(broadcast_system_stats())
        asyncio.create_task(broadcast_weather_stats())
        asyncio.create_task(broadcast_music_stats())
        asyncio.create_task(broadcast_ha_stats())
        
        # Le gestionnaire de parole est déjà lancé au démarrage du script

        
        async with websockets.serve(ws_handler, "0.0.0.0", 8765):
            await asyncio.Future()

    threading.Thread(target=lambda: asyncio.run(start_ws()), daemon=True).start()

    # On attend un tout petit peu que le thread WS soit prêt
    time.sleep(1.5)
    # Accueil vocal
    speech.parler("Tous mes systèmes sont opérationnels.")

    
    # On lance l'écoute (qui est bloquante dans ce thread)
    ecouter()


# ==========================================
# LANCEMENT — MODE CONSOLE + FRONTEND WEB
# ==========================================
# Ursina desactive : l'interface est maintenant le frontend Three.js
# dans le dossier frontend/ (npm run dev -> http://localhost:5173)
# Le WebSocket est deja demarre par start_ia() sur ws://localhost:8765

if pygame:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
else:
    print("[INFO] Pygame absent — demarrage sans audio TTS.")

def start_mobile_http_server():
    """Serveur HTTP minimal pour servir l'interface mobile sur le port 8080."""
    import http.server
    mobile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile")
    if not os.path.exists(mobile_dir):
        print("[MOBILE] Dossier mobile/ introuvable, serveur non demarre.")
        return
    class MobileHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=mobile_dir, **kwargs)
        def log_message(self, format, *args):
            pass  # Silencieux
    server = http.server.HTTPServer(("0.0.0.0", 8080), MobileHandler)
    print("[MOBILE] Serveur HTTP mobile démarré.")
    server.serve_forever()

def liberer_port(port):
    """Tue le processus qui occupe le port donné (Windows)."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True
        )
        stdout = result.stdout.decode(errors='ignore')
        for line in stdout.splitlines():
            if f":{port}" in line and ("LISTENING" in line or "ÉCOUTE" in line):
                parts = line.strip().split()
                pid = parts[-1]
                if pid.isdigit() and int(pid) != os.getpid():
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
                    print(f"[DÉMARRAGE] Port {port} libéré (PID {pid} terminé).")
                    return
    except Exception as e:
        print(f"[DÉMARRAGE] Impossible de libérer le port {port} : {e}")

def main():
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        console = Console()
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[cyan]⚙  Backend[/cyan]", "[green]Actif (Terminal)[/green]")
        table.add_row("[cyan]🌐  WebSocket (Local)[/cyan]", "[green]ws://localhost:8765[/green]")
        table.add_row("[cyan]🌐  WebSocket (Réseau)[/cyan]", f"[green]ws://{LOCAL_IP}:8765[/green]")
        table.add_row("[cyan]📱  Interface Mobile[/cyan]", f"[green]http://{LOCAL_IP}:8080[/green]")
        table.add_row("[cyan]🎙  Commande Vocale[/cyan]", "[yellow]Active (Mot-clé: 'Jarvis')[/yellow]")
        
        print()
        console.print(Panel(
            table,
            title="[bold green]✔  STATUT DES SERVICES[/bold green]",
            border_style="green",
            expand=False
        ))
        print()
    except Exception:
        print("  Backend   : actif (terminal)")
        print(f"  WebSocket : ws://localhost:8765  (LAN: ws://{LOCAL_IP}:8765)")
        print(f"  Mobile    : http://{LOCAL_IP}:8080")
        print()
        print("  Commandes vocales actives.")
        print("  Dites 'Jarvis' pour activer la session.")
        print("=" * 60)
        print()

    # Initialisation Système d'Alarmes
    set_parler_callback(parler)
    demarrer_daemon_alarmes()
    
    # Lancement de la découverte TV en arrière-plan (non-bloquant)
    import threading
    # Plus besoin de découverte TV avec le mode ADB Direct

    # Liberer les ports si une instance precedente tourne encore
    # Un seul appel netstat pour les 3 ports (évite 3x ~1.5s de latence)
    _ports_a_liberer = [8765, 8080, 5173]
    try:
        _result = subprocess.run(["netstat", "-ano"], capture_output=True)
        _stdout = _result.stdout.decode(errors='ignore')
        for _line in _stdout.splitlines():
            for _port in _ports_a_liberer:
                if f":{_port}" in _line and ("LISTENING" in _line or "ÉCOUTE" in _line):
                    _parts = _line.strip().split()
                    _pid = _parts[-1]
                    if _pid.isdigit() and int(_pid) != os.getpid():
                        subprocess.run(["taskkill", "/F", "/PID", _pid], capture_output=True)
                        print(f"[DÉMARRAGE] Port {_port} libéré (PID {_pid} terminé).")
    except Exception as _e:
        print(f"[DÉMARRAGE] Impossible de libérer les ports : {_e}")

    # Lancer le serveur Frontend
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    frontend_process = None
    FRONTEND_URL = "http://localhost:5173"

    def _port_ecoute(port, timeout=4.0):
        """Retourne True si quelque chose ecoute sur le port donne."""
        import socket
        debut = time.time()
        while time.time() - debut < timeout:
            for host in ("localhost", "127.0.0.1", "::1"):
                try:
                    with socket.create_connection((host, port), timeout=0.3):
                        return True
                except (ConnectionRefusedError, OSError):
                    pass
            time.sleep(0.2)
        return False

    def _servir_dist_python(port=5173):
        """Sert le dossier dist/ avec le serveur HTTP Python (fallback sans npm)."""
        import http.server, socketserver
        dist_dir = os.path.join(frontend_dir, "dist")
        os.chdir(dist_dir)
        handler = http.server.SimpleHTTPRequestHandler
        handler.log_message = lambda *a: None  # silencieux
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"[JARVIS] Frontend servi via Python HTTP sur http://localhost:{port}")
            httpd.serve_forever()

    vite_ok = False
    if os.path.exists(frontend_dir):
        # Tentative 1 : Vite (npm run dev)
        try:
            print("[JARVIS] Tentative de lancement Vite (npm run dev)...")
            log_path = os.path.join(frontend_dir, "vite_output.log")
            with open(log_path, "w", encoding="utf-8") as f_log:
                frontend_process = subprocess.Popen(
                    ["npm", "run", "dev"], cwd=frontend_dir, shell=True,
                    stdout=f_log, stderr=f_log
                )
            # Timeout augmenté légèrement à 6.0s au cas où le système ralentit
            vite_ok = _port_ecoute(5173, timeout=6.0)
            if vite_ok:
                print("[JARVIS] Interface locale (Vite) initialisée.")
            else:
                print("[JARVIS] Vite n'a pas demarre (npm/vite absent ou erreur).")
                if frontend_process:
                    frontend_process.terminate()
                    frontend_process = None
                # Afficher le contenu des logs en cas d'échec
                try:
                    if os.path.exists(log_path):
                        with open(log_path, "r", encoding="utf-8") as f_log:
                            logs = f_log.read().strip()
                            if logs:
                                print("[JARVIS] --- LOGS VITE ---")
                                print(logs)
                                print("[JARVIS] -----------------")
                except Exception:
                    pass
        except Exception as e:
            print(f"[JARVIS] Impossible de lancer Vite : {e}")
            frontend_process = None

        # Tentative 2 : servir dist/ avec Python (pas besoin de npm)
        if not vite_ok:
            dist_dir = os.path.join(frontend_dir, "dist")
            if os.path.exists(dist_dir) and os.path.exists(os.path.join(dist_dir, "index.html")):
                print("[JARVIS] Fallback : service du dossier dist/ via Python HTTP...")
                t_dist = threading.Thread(target=_servir_dist_python, args=(5173,), daemon=True)
                t_dist.start()
                vite_ok = _port_ecoute(5173, timeout=3.0)
                if vite_ok:
                    print("[JARVIS] Frontend dist/ servi correctement.")
            else:
                print("[JARVIS] Aucun dossier dist/ trouve. Interface non disponible.")
                print("[JARVIS] Pour corriger : cd frontend && npm install && npm run build")

    if not vite_ok:
        print("[JARVIS] ATTENTION : l'interface visuelle ne sera pas disponible.")
        print("[JARVIS] JARVIS reste fonctionnel en mode vocal uniquement.")

    # Verification initiale des mises a jour
    verifier_mises_a_jour()
    
    # Lancer les services en arriere-plan
    threading.Thread(target=start_mobile_http_server, daemon=True).start()
    threading.Thread(target=start_ia, daemon=True).start()
    threading.Thread(target=verifier_mises_a_jour_loop, daemon=True).start()

    # Choisir le mode d'affichage
    use_native = _WEBVIEW_OK and webview is not None and not FORCE_BROWSER_MODE

    if use_native:
        # MODE FENETRE NATIVE (pywebview)
        print("[JARVIS] Ouverture dans une fenetre native (pywebview)...")

        # Calcul de la taille et position centrée selon la résolution de l'écran
        try:
            from screeninfo import get_monitors
            _mon = get_monitors()[0]
            _sw, _sh = _mon.width, _mon.height
        except Exception:
            _sw, _sh = 1920, 1080

        # 85% de l'écran, min 1280x780
        _win_w = max(1280, int(_sw * 0.85))
        _win_h = max(780,  int(_sh * 0.85))
        _win_x = (_sw - _win_w) // 2
        _win_y = (_sh - _win_h) // 2

        global _WEBVIEW_WINDOW
        _WEBVIEW_WINDOW = webview.create_window(
            title            = "J.A.R.V.I.S",
            url              = FRONTEND_URL,
            width            = _win_w,
            height           = _win_h,
            x                = _win_x,
            y                = _win_y,
            resizable        = True,
            min_size         = (900, 600),
            background_color = "#0a0a0f",
        )

        def _on_closed():
            print("\n[JARVIS] Fenetre fermee — extinction du systeme...")
            if frontend_process:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

        _WEBVIEW_WINDOW.events.closed += _on_closed

        def _on_loaded():
            try:
                import ctypes
                import os
                # Groupement dans la barre des taches (detache de python.exe)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TechEnClair.Jarvis.App")
                
                # Remplacement de l'icone de la fenetre webview
                hwnd = ctypes.windll.user32.FindWindowW(None, "J.A.R.V.I.S")
                if hwnd:
                    icon_path = os.path.abspath("jarvis.ico")
                    if os.path.exists(icon_path):
                        hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x0010)
                        if hicon:
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon) # ICON_SMALL
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon) # ICON_BIG
            except Exception as e:
                print(f"[JARVIS] Erreur chargement icone : {e}")

        _WEBVIEW_WINDOW.events.loaded += _on_loaded

        # webview.start() DOIT etre appele depuis le thread principal
        try:
            # Desactive le mode prive (private_mode=False) et definit le storage_path persistant pour conserver les permissions
            _app_data = os.getenv("APPDATA", os.path.expanduser("~"))
            _storage_path = os.path.join(_app_data, "JARVIS")
            webview.start(private_mode=False, storage_path=_storage_path)
        except Exception as e:
            print(f"[JARVIS] PyWebView impossible : {e} — bascule sur navigateur")
            _ouvrir_dans_navigateur(FRONTEND_URL, frontend_process)
    else:
        # MODE NAVIGATEUR (fallback si pywebview absent)
        _ouvrir_dans_navigateur(FRONTEND_URL, frontend_process)


def _trouver_chemin_navigateur():
    """Tente de trouver le chemin de Chrome ou Edge pour le mode --app."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def _ouvrir_dans_navigateur(url, frontend_process):
    """
    Ouvre JARVIS dans un navigateur, de préférence en mode 'app' (sans barres).
    """
    print(f"[JARVIS] Preparation de l'interface sur {url}...")
    navigateur = _trouver_chemin_navigateur()
    
    if navigateur:
        print(f"[JARVIS] Lancement du mode App (sans bordures) avec profil persistant via : {os.path.basename(navigateur)}")
        try:
            profile_path = r"C:\Users\mylan\.gemini\antigravity\chrome_profile"
            if not os.path.exists(profile_path):
                os.makedirs(profile_path, exist_ok=True)
            subprocess.Popen([navigateur, f"--app={url}", f"--user-data-dir={profile_path}"])
        except Exception as e:
            print(f"[JARVIS] Erreur lors du lancement mode App, fallback standard : {e}")
            import webbrowser
            webbrowser.open(url)
    else:
        print(f"[JARVIS] Aucun navigateur compatible App trouve. Ouverture standard...")
        import webbrowser
        webbrowser.open(url)
    
    _attendre_interface(frontend_process)

def _attendre_interface(frontend_process):
    """Gère la boucle d'attente et l'extinction du système."""
    try:
        while True:
            time.sleep(1)
            # On ne ferme que si l'interface a été connectée au moins une fois
            if interface_deja_connectee and len(CONNECTED_CLIENTS) == 0:
                print("\n[JARVIS] Interface deconnectee. Attente de reconnexion (60s)...")
                time.sleep(60)
                if len(CONNECTED_CLIENTS) == 0:
                    print("[JARVIS] Aucune reconnexion. Extinction automatique...")
                    break
                else:
                    print("[JARVIS] Reconnexion detectee. Reprise.")
    except KeyboardInterrupt:
        print("\n[JARVIS] Arret manuel.")

    if frontend_process:
        print("[JARVIS] Arret du serveur Web...")
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )









# ==============================================================================
# SECTION PERSONNALISÉE : AJOUTS DE MYLANE
# Cette section contient la logique de gestion de la météo et du calendrier
# pour l'interface HUD Iron Man de JARVIS.
# ==============================================================================

async def envoyer_carte_contextuelle(titre: str, texte: str, type_carte: str = "info", icon: str = "◈", duree: int = 10000):
    """Envoie une carte dynamique au HUD via WebSocket."""
    if CONNECTED_CLIENTS:
        msg = json.dumps({
            "action": "ctx_card",
            "title": titre,
            "text": texte,
            "type": type_carte,
            "icon": icon,
            "duration": duree
        })
        await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)

# --- SIMULATION PROTOCOLE DOMOTIQUE (Maison de mylane) ---
SIMULATED_DOMOTIC_STATES = {
    # Lumières (1er Étage)
    "light.salon": "off",
    "light.plafond": "off",
    "light.canapes": "off",
    "light.lampadaire": "off",
    "light.lampe_de_chevet_2": "off",
    "light.grosse_boule": "off",
    "light.petite_boule": "off",
    "light.lsc_smart_led_strip_rgbic_cctic_5m": "off", # cuisine
    "light.cuisine_2": "off",
    "light.bureau": "off",
    "light.pc": "off",
    "light.pc_2": "off",
    "light.chambre_parentale": "off",
    "light.plafond_2": "off",
    
    # Prises (1er Étage)
    "switch.prise_salon": "off",
    "switch.prise_bureau": "off",
    "switch.prise_cuisine": "off",
    
    # Nouvelles entités dessinées par Mylan
    "light.veranda": "off",
    "light.sdb_parents": "off",
    "light.garage": "off",
    "light.couloir": "off",
    "light.chambre_1": "off",
    "light.chambre_2": "off",
    "light.toilettes": "off",
    "light.sdb": "off",
    
    # Capteurs de Températures
    "temp.salon": 20.5,
    "temp.cuisine": 21.2,
    "temp.parents": 19.8,
    "temp.veranda": 16.8,
    "temp.garage": 14.5,
    "temp.couloir": 19.5,
    "temp.chambre_1": 20.0,
    "temp.chambre_2": 20.2,
    "temp.sdb": 22.5,
}

async def broadcast_ha_stats():
    """Diffuse périodiquement les états domotiques de simulation."""
    import random
    while True:
        try:
            if CONNECTED_CLIENTS:
                # Simuler de légères variations de température (+- 0.05°C)
                for room in ["salon", "cuisine", "parents", "veranda", "garage", "couloir", "chambre_1", "chambre_2", "sdb"]:
                    key = f"temp.{room}"
                    SIMULATED_DOMOTIC_STATES[key] += random.choice([-0.05, 0.0, 0.05])
                    SIMULATED_DOMOTIC_STATES[key] = round(max(10.0, min(30.0, SIMULATED_DOMOTIC_STATES[key])), 2)
                
                msg = json.dumps({
                    "action": "domotic_map_update",
                    "states": {k: {"state": v} for k, v in SIMULATED_DOMOTIC_STATES.items()}
                })
                # Broadcast
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
        except Exception as e:
            print(f"[DOMOTIC SIM] Erreur broadcast: {e}")
        await asyncio.sleep(6)

async def handle_domotic_sim_ws(data, websocket):
    """Gère les messages WebSocket spatial_action domotique."""
    action = data.get("action")
    if action == "domotic_list":
        # Envoyer l'état complet actuel
        msg = json.dumps({
            "action": "domotic_map_update",
            "states": {k: {"state": v} for k, v in SIMULATED_DOMOTIC_STATES.items()}
        })
        await websocket.send(msg)
    elif action == "domotic_toggle":
        entity_id = data.get("entity_id")
        if entity_id in SIMULATED_DOMOTIC_STATES:
            curr = SIMULATED_DOMOTIC_STATES[entity_id]
            new_val = "off" if curr == "on" else "on"
            SIMULATED_DOMOTIC_STATES[entity_id] = new_val
            print(f"[DOMOTIC SIM] Toggle {entity_id} -> {new_val}")
            
            # Diffuser immédiatement la mise à jour à tous les clients
            msg = json.dumps({
                "action": "domotic_map_update",
                "states": {k: {"state": v} for k, v in SIMULATED_DOMOTIC_STATES.items()}
            })
            await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)

async def handle_cortex_ws(data, websocket):
    """Gère les messages WebSocket spatial_action du Cortex Neuronal."""
    action = data.get("action")
    if action == "cortex_list":
        import module.vector_memory as vector_memory
        souvenirs_vecteurs = []
        
        # 1. Souvenirs vectoriels ChromaDB
        for s in vector_memory.lister_souvenirs_complets():
            doc_text = s.get("document", "")
            entry_id = s.get("id", "")
            user_text = doc_text
            model_text = ""
            timestamp = s.get("metadata", {}).get("timestamp", "Date inconnue")
            
            try:
                lines = doc_text.split("\n")
                for line in lines:
                    if line.startswith("Date: "):
                        timestamp = line[6:].strip()
                    elif line.startswith("User: "):
                        user_text = line[6:].strip()
                    elif line.startswith("Assistant: "):
                        model_text = line[11:].strip()
            except Exception:
                pass
                
            souvenirs_vecteurs.append({
                "id": entry_id,
                "type": "vector",
                "user": user_text,
                "assistant": model_text,
                "timestamp": timestamp
            })

        # 2. Souvenirs locaux clé-valeur
        souvenirs_kv = []
        mem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_memoire.json")
        if os.path.exists(mem_path):
            try:
                with open(mem_path, "r", encoding="utf-8") as f:
                    kv_data = json.load(f)
                    for key, val_obj in kv_data.items():
                        val = val_obj.get("valeur", "")
                        t_stamp = val_obj.get("timestamp", "Date inconnue")
                        souvenirs_kv.append({
                            "id": f"kv_{key}",
                            "type": "key_value",
                            "user": f"Fait retenu : {key}",
                            "assistant": f"Valeur mémorisée : {val}",
                            "timestamp": t_stamp
                        })
            except Exception as err:
                print(f"[CORTEX] Erreur lecture jarvis_memoire.json : {err}")
                
        # Charger les synapses personnalisées créées par Drag-and-Link
        synapses_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_synapses.json")
        custom_links = []
        if os.path.exists(synapses_path):
            try:
                with open(synapses_path, "r", encoding="utf-8") as f:
                    custom_links = json.load(f)
            except Exception as err:
                print(f"[CORTEX] Erreur lecture jarvis_synapses.json : {err}")

        # Envoi au client
        msg = json.dumps({
            "action": "cortex_list",
            "nodes": souvenirs_vecteurs + souvenirs_kv,
            "links": custom_links
        })
        await websocket.send(msg)


    elif action == "cortex_edit_memory":
        souvenir_id = data.get("entity_id")
        user_txt = data.get("user", "")
        assistant_txt = data.get("assistant", "")
        if not souvenir_id:
            return
            
        edited_ok = False
        if souvenir_id.startswith("kv_"):
            # Édition clé-valeur locale (Fait)
            key = souvenir_id[3:]
            new_key = user_txt.replace("Fait retenu : ", "").strip()
            new_val = assistant_txt.replace("Valeur mémorisée : ", "").strip()
            
            mem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_memoire.json")
            if os.path.exists(mem_path):
                try:
                    with open(mem_path, "r", encoding="utf-8") as f:
                        kv_data = json.load(f)
                    
                    if key in kv_data:
                        t_stamp = kv_data[key].get("timestamp", datetime.now().strftime("%d/%m/%Y %H:%M"))
                        if key != new_key:
                            del kv_data[key]
                        kv_data[new_key] = {
                            "valeur": new_val,
                            "timestamp": t_stamp
                        }
                        with open(mem_path, "w", encoding="utf-8") as f:
                            json.dump(kv_data, f, ensure_ascii=False, indent=2)
                        edited_ok = True
                        print(f"[CORTEX] Modifié fait local : {key} -> {new_key} = {new_val}")
                except Exception as err:
                    print(f"[CORTEX] Erreur édition fait local : {err}")
        else:
            # Édition vectorielle ChromaDB
            try:
                import module.vector_memory as vector_memory
                coll = vector_memory._get_collection()
                if coll:
                    res = coll.get(ids=[souvenir_id])
                    t_stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                    if res and res.get('documents') and res['documents'][0]:
                        doc_text = res['documents'][0][0]
                        for line in doc_text.split("\n"):
                            if line.startswith("Date: "):
                                t_stamp = line[6:].strip()
                                break
                    
                    new_doc = f"Date: {t_stamp}\nUser: {user_txt}\nAssistant: {assistant_txt}"
                    coll.update(ids=[souvenir_id], documents=[new_doc])
                    edited_ok = True
                    print(f"[CORTEX] Modifié souvenir vectoriel : {souvenir_id}")
            except Exception as err:
                print(f"[CORTEX] Erreur édition souvenir vectoriel : {err}")
                
        if edited_ok:
            # Diffuser la mise à jour à tous les clients connectés
            msg = json.dumps({
                "action": "cortex_edit_success",
                "entity_id": souvenir_id,
                "user": user_txt,
                "assistant": assistant_txt
            })
            await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)


    elif action == "cortex_delete":
        souvenir_id = data.get("entity_id")
        if not souvenir_id:
            return
            
        deleted_ok = False
        if souvenir_id.startswith("kv_"):
            # Suppression clé-valeur locale
            key_to_delete = souvenir_id[3:]
            mem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_memoire.json")
            if os.path.exists(mem_path):
                try:
                    with open(mem_path, "r", encoding="utf-8") as f:
                        kv_data = json.load(f)
                    if key_to_delete in kv_data:
                        del kv_data[key_to_delete]
                        with open(mem_path, "w", encoding="utf-8") as f:
                            json.dump(kv_data, f, ensure_ascii=False, indent=2)
                        deleted_ok = True
                        print(f"[CORTEX] Supprimé clé locale : {key_to_delete}")
                except Exception as err:
                    print(f"[CORTEX] Erreur suppression clé locale : {err}")
        else:
            # Suppression vectorielle ChromaDB
            try:
                import module.vector_memory as vector_memory
                coll = vector_memory._get_collection()
                if coll:
                    coll.delete(ids=[souvenir_id])
                    deleted_ok = True
                    print(f"[CORTEX] Supprimé souvenir vectoriel : {souvenir_id}")
            except Exception as err:
                print(f"[CORTEX] Erreur suppression souvenir vectoriel : {err}")
                
        if deleted_ok:
            # Diffuser le signal de mise à jour à tous les clients connectés
            msg = json.dumps({
                "action": "cortex_update",
                "deleted_id": souvenir_id
            })
            await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)

    elif action == "cortex_speak":
        souvenir_id = data.get("entity_id")
        if not souvenir_id:
            return
            
        phrase = ""
        if souvenir_id.startswith("kv_"):
            # Fait local clé-valeur
            key = souvenir_id[3:]
            mem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_memoire.json")
            if os.path.exists(mem_path):
                try:
                    with open(mem_path, "r", encoding="utf-8") as f:
                        kv_data = json.load(f)
                    if key in kv_data:
                        valeur = kv_data[key].get("valeur", "")
                        timestamp = kv_data[key].get("timestamp", "Date inconnue")
                        phrase = f"Fait mémorisé le {timestamp}. Pour la clé : {key}. La valeur enregistrée est : {valeur}."
                except Exception as err:
                    print(f"[CORTEX] Erreur lecture fait local pour parler : {err}")
        else:
            # Souvenir vectoriel ChromaDB
            try:
                import module.vector_memory as vector_memory
                coll = vector_memory._get_collection()
                if coll:
                    res = coll.get(ids=[souvenir_id])
                    if res and res.get('documents') and res['documents'][0]:
                        doc_text = res['documents'][0][0]
                        timestamp = "Date inconnue"
                        user_text = doc_text
                        model_text = ""
                        
                        lines = doc_text.split("\n")
                        for line in lines:
                            if line.startswith("Date: "):
                                timestamp = line[6:].strip()
                            elif line.startswith("User: "):
                                user_text = line[6:].strip()
                            elif line.startswith("Assistant: "):
                                model_text = line[11:].strip()
                        
                        if model_text:
                            phrase = f"Souvenir conversationnel du {timestamp}. Vous m'avez dit : {user_text}. Et je vous ai répondu : {model_text}."
                        else:
                            phrase = f"Souvenir conversationnel du {timestamp}. Échange mémorisé : {user_text}."
            except Exception as err:
                print(f"[CORTEX] Erreur lecture souvenir vectoriel pour parler : {err}")
                
        if phrase:
            builtins.parler(phrase, print_console=True)

    elif action == "cortex_link":
        from_id = data.get("from_id")
        to_id = data.get("to_id")
        if from_id and to_id:
            synapses_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_synapses.json")
            custom_links = []
            if os.path.exists(synapses_path):
                try:
                    with open(synapses_path, "r", encoding="utf-8") as f:
                        custom_links = json.load(f)
                except:
                    pass
            # Éviter les doublons de liaison
            exists = any(
                (l.get("from") == from_id and l.get("to") == to_id) or 
                (l.get("from") == to_id and l.get("to") == from_id) 
                for l in custom_links
            )
            if not exists:
                custom_links.append({"from": from_id, "to": to_id})
                try:
                    with open(synapses_path, "w", encoding="utf-8") as f:
                        json.dump(custom_links, f, ensure_ascii=False, indent=2)
                    print(f"[CORTEX] Liaison synaptique créée : {from_id} <-> {to_id}")
                    # Diffuser la liaison à tous les clients connectés
                    msg = json.dumps({
                        "action": "cortex_link_created",
                        "from": from_id,
                        "to": to_id
                    })
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                except Exception as err:
                    print(f"[CORTEX] Erreur écriture jarvis_synapses.json : {err}")
            else:
                # Supprimer la liaison existante !
                custom_links = [
                    l for l in custom_links 
                    if not ((l.get("from") == from_id and l.get("to") == to_id) or 
                            (l.get("from") == to_id and l.get("to") == from_id))
                ]
                try:
                    with open(synapses_path, "w", encoding="utf-8") as f:
                        json.dump(custom_links, f, ensure_ascii=False, indent=2)
                    print(f"[CORTEX] Liaison synaptique supprimée : {from_id} <-> {to_id}")
                    # Diffuser la suppression à tous les clients
                    msg = json.dumps({
                        "action": "cortex_link_removed",
                        "from": from_id,
                        "to": to_id
                    })
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                except Exception as err:
                    print(f"[CORTEX] Erreur écriture jarvis_synapses.json : {err}")


async def broadcast_cortex_new_memory(user_text, model_text):
    """Diffuse la création d'un souvenir en direct pour animer le Cortex."""
    timestamp = time.strftime("%d/%m/%Y %H:%M")
    entry_id = f"msg_{int(time.time())}"
    msg = json.dumps({
        "action": "cortex_new_memory",
        "node": {
            "id": entry_id,
            "type": "vector",
            "user": user_text,
            "assistant": model_text,
            "timestamp": timestamp
        }
    })
    if CONNECTED_CLIENTS:
        await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)

# Callback hook synchrone -> asynchrone vers le WebSocket
def _notify_cortex_new_memory(user_text, model_text):
    if WS_LOOP and CONNECTED_CLIENTS:
        asyncio.run_coroutine_threadsafe(
            broadcast_cortex_new_memory(user_text, model_text),
            WS_LOOP
        )

import module.vector_memory as _vm
_vm.on_souvenir_added.append(_notify_cortex_new_memory)

def _notify_factual_memory_added(cle, valeur):
    """Diffuse la création d'un fait mémorisé en direct au Cortex."""
    timestamp = time.strftime("%d/%m/%Y %H:%M")
    node = {
        "id": f"kv_{cle}",
        "type": "key_value",
        "user": f"Fait retenu : {cle}",
        "assistant": f"Valeur mémorisée : {valeur}",
        "timestamp": timestamp
    }
    msg = json.dumps({
        "action": "cortex_new_memory",
        "node": node
    })
    _safe_ws_send(msg)

import builtins
builtins._notify_factual_memory_added = _notify_factual_memory_added
builtins.envoyer_carte_contextuelle = envoyer_carte_contextuelle

async def broadcast_system_stats():
    """Diffuse les stats CPU/RAM et envoie des alertes contextuelles si nécessaire."""
    last_alert_time = 0
    while True:
        try:
            if CONNECTED_CLIENTS:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                # Stats classiques (pour les jauges)
                msg = json.dumps({"action": "system_stats", "cpu": cpu, "ram": ram})
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                
                # Alerte contextuelle si CPU > 90%
                if cpu > 90 and (time.time() - last_alert_time > 60):
                    await envoyer_carte_contextuelle(
                        "Alerte Système",
                        f"Charge CPU critique détectée : {cpu}%. Les performances de JARVIS peuvent être affectées.",
                        type_carte="alert",
                        icon="⚠",
                        duree=15000
                    )
                    last_alert_time = time.time()
        except Exception:
            pass
        await asyncio.sleep(2)

_location_cfg = _charger_config()
CLIENT_LOCATION = {
    "lat": _location_cfg.get("latitude", 45.2917),
    "lon": _location_cfg.get("longitude", 4.1722),
    "city": "Monistrol-sur-Loire"
} 

async def update_client_city():
    global CLIENT_LOCATION
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={CLIENT_LOCATION['lat']}&lon={CLIENT_LOCATION['lon']}&format=json"
        headers = {"User-Agent": "JARVIS-Assistant/1.0"}
        resp = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("address", {}).get("city") or data.get("address", {}).get("town") or data.get("address", {}).get("village") or "Ma position"
            CLIENT_LOCATION["city"] = city
            print(f"[METEO] Localisation mise a jour : {city}")
    except Exception as e:
        print(f"[METEO] Erreur reverse geocoding : {e}")

async def get_weather_fallback_wttr(city_name):
    try:
        url = f"https://wttr.in/{requests.utils.quote(city_name)}?format=j1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        resp = await asyncio.to_thread(requests.get, url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current_condition", [{}])[0]
            day = data.get("weather", [{}])[0]
            
            desc = curr.get("weatherDesc", [{}])[0].get("value", "Inconnu")
            translations = {
                "sunny": "Ensoleillé", "clear": "Clair", "partly cloudy": "Partiellement nuageux",
                "cloudy": "Nuageux", "overcast": "Couvert", "mist": "Brume", "fog": "Brouillard",
                "patchy rain possible": "Possibilité de pluie", "patchy snow possible": "Possibilité de neige",
                "heavy rain": "Forte pluie", "light rain": "Pluie faible", "thunderstorm": "Orage"
            }
            desc_fr = translations.get(desc.lower(), desc)
            
            return {
                "city": city_name,
                "temp": float(curr.get("temp_C", 0)),
                "apparent": float(curr.get("FeelsLikeC", 0)),
                "humidity": float(curr.get("humidity", 0)),
                "wind": float(curr.get("windspeedKmph", 0)),
                "desc": desc_fr,
                "max": float(day.get("maxtempC", 0)),
                "min": float(day.get("mintempC", 0))
            }
    except Exception as e:
        print(f"[METEO] Échec du repli wttr.in pour {city_name} : {e}")
    return None

async def get_raw_weather(lat, lon, city_name):
    try:
        # print(f"[METEO] Recuperation pour {city_name} ({lat}, {lon})...")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weathercode",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto", "forecast_days": 1
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        resp = await asyncio.to_thread(requests.get, url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            cur = data["current"]
            day = data["daily"]
            from module.ha_config import CODES_METEO
            return {
                "city": city_name,
                "temp": cur["temperature_2m"],
                "apparent": cur["apparent_temperature"],
                "humidity": cur["relative_humidity_2m"],
                "wind": cur["wind_speed_10m"],
                "desc": CODES_METEO.get(cur["weathercode"], "Inconnu"),
                "max": day["temperature_2m_max"][0],
                "min": day["temperature_2m_min"][0]
            }
    except Exception:
        # Open-Meteo indisponible (SSL/timeout) → repli silencieux sur wttr.in
        wttr_weather = await get_weather_fallback_wttr(city_name)
        if wttr_weather:
            return wttr_weather
        # Les deux sources ont échoué — on loggue une seule fois
        print(f"[METEO] ⚠ Météo indisponible pour {city_name} (Open-Meteo + wttr.in KO).")
    return None

async def broadcast_weather_stats_once():
    """Diffuse la météo immédiatement sans attendre la boucle de 10 min."""
    if CONNECTED_CLIENTS:
        try:
            local_weather = await get_raw_weather(CLIENT_LOCATION["lat"], CLIENT_LOCATION["lon"], CLIENT_LOCATION["city"])
            if local_weather:
                msg = json.dumps({"action": "weather_update", "weather_type": "local", "weather": local_weather})
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
            
            mon_weather = await get_raw_weather(45.2917, 4.1722, "Monistrol-sur-Loire")
            if mon_weather:
                msg = json.dumps({"action": "weather_update", "weather_type": "monistrol", "weather": mon_weather})
                await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
        except Exception as e:
            print(f"[METEO] Erreur critique broadcast : {e}")

async def broadcast_weather_stats():
    """Diffuse la météo locale et celle de Monistrol périodiquement."""
    while True:
        try:
            if CONNECTED_CLIENTS:
                await broadcast_weather_stats_once()
        except Exception as e:
            print(f"[METEO] Erreur broadcast : {e}")
        await asyncio.sleep(600) # Toutes les 10 minutes

# Variables de suivi pour la progression
DEEZER_API_TOKEN = None
CURRENT_TRACK_ID = None
TRACK_START_TIME = None

async def get_deezer_api_token():
    """Récupère le jeton API nécessaire pour les requêtes Deezer via ARL."""
    global DEEZER_API_TOKEN
    arl = os.getenv("DEEZER_ARL")
    if not arl: return None
    try:
        url = "https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&api_version=1.0&api_token="
        cookies = {"arl": arl}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = await asyncio.to_thread(requests.get, url, cookies=cookies, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            DEEZER_API_TOKEN = data.get("results", {}).get("checkForm")
            return DEEZER_API_TOKEN
    except: pass
    return None

async def get_media_info_deezer_api():
    """Récupère le morceau en cours et estime la progression temporelle."""
    global DEEZER_API_TOKEN, CURRENT_TRACK_ID, TRACK_START_TIME
    arl = os.getenv("DEEZER_ARL")
    if not arl: return None

    if not DEEZER_API_TOKEN:
        await get_deezer_api_token()
    
    try:
        url = f"https://www.deezer.com/ajax/gw-light.php?method=user.getHistory&api_version=1.0&api_token={DEEZER_API_TOKEN}"
        cookies = {"arl": arl}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = await asyncio.to_thread(requests.get, url, cookies=cookies, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tracks = data.get("results", {}).get("data", [])
            if tracks:
                track = tracks[0]
                track_id = track.get("SNG_ID")
                title = track.get("SNG_TITLE", "INCONNU")
                artist = track.get("ART_NAME", "DEEZER")
                duration_sec = int(track.get("DURATION", 0))
                
                now = time.time()
                if track_id != CURRENT_TRACK_ID:
                    CURRENT_TRACK_ID = track_id
                    TRACK_START_TIME = now
                
                elapsed = int(now - TRACK_START_TIME)
                if elapsed > duration_sec: elapsed = duration_sec
                
                percent = (elapsed / duration_sec * 100) if duration_sec > 0 else 0
                
                def fmt_time(s):
                    m, s = divmod(int(s), 60)
                    return f"{m:02d}:{s:02d}"

                return {
                    "title": title.upper(),
                    "artist": artist.upper(),
                    "status": "Playing",
                    "position": fmt_time(elapsed),
                    "duration": fmt_time(duration_sec),
                    "percent": percent
                }
    except:
        DEEZER_API_TOKEN = None
    return None

async def get_media_info():
    """Récupère les infos média (Priorité UIA local, Fallback API Deezer, Fallback Windows)."""
    # 1. Tenter par UIA local (instantané et n'a pas besoin de réseau)
    try:
        info_local = await asyncio.to_thread(deezer_obtenir_titre_encours)
        if info_local:
            return {
                "title": info_local["title"].upper(),
                "artist": info_local["artist"].upper(),
                "status": "Playing",
                "position": "00:00",
                "duration": "00:00",
                "percent": 0
            }
    except Exception as uia_err:
        pass

    # 2. Fallback sur l'API Deezer en ligne
    info = await get_media_info_deezer_api()
    if info:
        return info


    import ctypes
    try:
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        titles = []
        def foreach_window(hwnd, lParam):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True
        ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)(foreach_window), 0)
        
        for t in titles:
            if "Deezer" in t and " - " in t:
                parts = t.split(" - ")
                return {
                    "title": parts[0].strip().upper(), 
                    "artist": parts[1].replace("Deezer","").strip().upper(), 
                    "status": "Playing"
                }
    except: pass
    return None

async def broadcast_music_stats():
    """Diffuse les infos Deezer/Media toutes les 2 secondes."""
    while True:
        try:
            if CONNECTED_CLIENTS:
                info = await get_media_info()
                if info:
                    msg = json.dumps({"action": "music_update", "data": info})
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
                else:
                    msg = json.dumps({"action": "music_update", "data": {"status": "Stopped", "title": "DEEZER_OFFLINE", "artist": "APPLICATION_NON_DETECTEE"}})
                    await asyncio.gather(*[ws.send(msg) for ws in CONNECTED_CLIENTS], return_exceptions=True)
        except Exception as e:
            pass
        await asyncio.sleep(2)

builtins.demander_ia_vision = demander_ia_vision
if __name__ == "__main__":
    main()
