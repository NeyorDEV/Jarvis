"""
JARVIS — TTS local via Kokoro-82M (ONNX, ultra-rapide)

Charge le modèle Kokoro-82M au démarrage et génère la voix en français
en moins de 100ms sur GPU (ou ~1s sur CPU) en remplacement de l'ancien F5-TTS.
"""

import os
import time
import soundfile as sf
import onnxruntime as ort
from kokoro_onnx import Kokoro

# ── Chemins ───────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KOKORO_DIR = os.path.join(_BASE_DIR, "core", "kokoro")
MODEL_PATH = os.path.join(_KOKORO_DIR, "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join(_KOKORO_DIR, "voices-v1.0.bin")

# ── Modèle (chargé une seule fois) ───────────────────────────────────────────
_kokoro_pipeline = None
_ready = False


def init_tts() -> bool:
    """Charge le modèle Kokoro-82M ONNX. Appelé au démarrage de JARVIS."""
    global _kokoro_pipeline, _ready

    if _ready:
        return True

    if not os.path.exists(MODEL_PATH) or not os.path.exists(VOICES_PATH):
        print(f"❌ [🗣 Kokoro-TTS] Fichiers du modèle introuvables dans {_KOKORO_DIR}")
        return False

    try:
        print("⚡ [🗣 Kokoro-TTS] Initialisation du moteur vocal (ONNX Runtime)...")
        
        # Ajout manuel des répertoires DLL pour Windows (CUDA + cuDNN)
        if os.name == 'nt':
            cuda_bin = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9\bin"
            cudnn_bin = r"C:\Program Files\NVIDIA\CUDNN\v9.23\bin\12.9\x64"
            if os.path.exists(cuda_bin):
                os.add_dll_directory(cuda_bin)
                os.environ["PATH"] = cuda_bin + os.pathsep + os.environ["PATH"]
            if os.path.exists(cudnn_bin):
                os.add_dll_directory(cudnn_bin)
                os.environ["PATH"] = cudnn_bin + os.pathsep + os.environ["PATH"]

        # Tentative d'utilisation de CUDA si supporté, sinon fallback CPU automatique
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        
        # Désactiver les avertissements globaux d'ONNX Runtime (warnings de recopie mémoire ou d'opérateurs)
        try:
            ort.set_default_logger_severity(3) # 3 = Error
        except:
            pass
        
        so = ort.SessionOptions()
        so.log_severity_level = 3 # 3 = Severe / Error only
        
        session = ort.InferenceSession(MODEL_PATH, providers=providers, sess_options=so)
        print(f"✔ [🗣 Kokoro-TTS] Moteur activé sur : {session.get_providers()}")
        
        _kokoro_pipeline = Kokoro.from_session(session, VOICES_PATH)
        _ready = True
        print("✔ [🗣 Kokoro-TTS] Synthèse vocale locale opérationnelle.")
        return True

    except Exception as e:
        print(f"❌ [🗣 Kokoro-TTS] Échec du chargement : {e}")
        _ready = False
        return False


def generer_audio(texte: str, output_path: str) -> bool:
    """
    Génère un fichier WAV à output_path à partir du texte en français,
    en utilisant la voix féminine française ff_siwis.
    """
    global _kokoro_pipeline, _ready

    if not _ready:
        if not init_tts():
            return False

    if not texte or not texte.strip():
        return False

    try:
        t0 = time.monotonic()
        
        # Nettoyage minimal du texte pour la phonémisation
        texte_propre = texte.replace("**", "").replace("*", "").replace("`", "").strip()
        
        # Synthèse via Kokoro
        # ff_siwis = French Female voice (seule voix française native de Kokoro v1.0)
        samples, sample_rate = _kokoro_pipeline.create(
            texte_propre,
            voice="ff_siwis",
            speed=1.0,
            lang="fr-fr"
        )
        
        # Sauvegarde au format WAV
        sf.write(output_path, samples, sample_rate)
        
        print(f"✔ [🗣 Kokoro-TTS] Parole générée en {time.monotonic()-t0:.2f}s")
        return True

    except Exception as e:
        print(f"❌ [🗣 Kokoro-TTS] Erreur de génération vocale : {e}")
        return False
