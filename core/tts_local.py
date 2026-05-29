"""
JARVIS — TTS local via F5-TTS (clone de voix, GPU CUDA)

Charge le modèle une seule fois au démarrage, génère ensuite
chaque phrase en ~4s sur RTX 4070 Super.

IMPORTANT :
- Ne pas appeler torch.cuda avant d'importer F5TTS → ACCESS_VIOLATION.
- Ne pas laisser ref_text="" → F5-TTS appelle torchcodec (DLLs manquantes sur Windows).
  Solution : fournir ref_text depuis jarvis_voice.txt (ou texte par défaut).
- Fichier référence : jarvis_voice.wav (24kHz mono, converti depuis MP3 via ffmpeg)
"""

import os
import time
import soundfile as sf

# ── Chemins ───────────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_SAMPLE = os.path.join(_BASE_DIR, "jarvis_voice.wav")   # WAV 24kHz mono
VOICE_TEXT   = os.path.join(_BASE_DIR, "jarvis_voice.txt")   # Transcription du sample

# Texte par défaut si jarvis_voice.txt est absent
_DEFAULT_REF_TEXT = "Bien sûr Monsieur. Je suis prêt à vous assister en toutes circonstances."

# ── Modèle (chargé une seule fois) ───────────────────────────────────────────
_model = None
_ready = False
_ref_text_cache: str | None = None


def _charger_ref_text() -> str:
    """Charge la transcription du sample depuis jarvis_voice.txt (ou texte par défaut)."""
    global _ref_text_cache
    if _ref_text_cache is not None:
        return _ref_text_cache
    if os.path.exists(VOICE_TEXT):
        with open(VOICE_TEXT, "r", encoding="utf-8") as f:
            _ref_text_cache = f.read().strip()
            print(f"[TTS LOCAL] ref_text chargé depuis {VOICE_TEXT}")
    else:
        _ref_text_cache = _DEFAULT_REF_TEXT
        print(f"[TTS LOCAL] jarvis_voice.txt absent — ref_text par défaut utilisé")
    return _ref_text_cache


def init_tts():
    """Charge F5-TTS en VRAM. Appelé une fois au démarrage de JARVIS."""
    global _model, _ready

    if _ready:
        return True

    try:
        print("[TTS LOCAL] Chargement F5-TTS sur GPU...")
        from f5_tts.api import F5TTS

        # NE PAS appeler torch.cuda.is_available() avant F5TTS : provoque un ACCESS_VIOLATION.
        # On tente directement CUDA, fallback CPU si erreur.
        try:
            _model = F5TTS(device="cuda")
            print("[TTS LOCAL] Device : cuda (RTX 4070 Super)")
        except Exception:
            _model = F5TTS(device="cpu")
            print("[TTS LOCAL] Device : cpu (CUDA indisponible)")

        _charger_ref_text()  # Précharge le texte de référence
        _ready = True
        print("[TTS LOCAL] F5-TTS prêt.")
        return True

    except Exception as e:
        print(f"[TTS LOCAL] Erreur chargement : {e}")
        _ready = False
        return False


def generer_audio(texte: str, output_path: str) -> bool:
    """
    Génère un fichier WAV à output_path à partir du texte,
    en clonant la voix de jarvis_voice.wav.
    Retourne True si succès.

    NOTE : ref_text est fourni explicitement pour éviter la transcription
    automatique via torchcodec (DLLs absentes sous Windows).
    """
    global _model, _ready

    if not _ready:
        if not init_tts():
            return False

    if not os.path.exists(VOICE_SAMPLE):
        print(f"[TTS LOCAL] Sample introuvable : {VOICE_SAMPLE}")
        return False

    try:
        t0 = time.monotonic()
        ref_text = _charger_ref_text()

        wav, sr, _ = _model.infer(
            ref_file=VOICE_SAMPLE,
            ref_text=ref_text,    # Fourni explicitement : évite torchcodec (transcription auto)
            gen_text=texte,
            target_rms=0.1,
            cross_fade_duration=0.15,
            speed=1.0,
            fix_duration=None,
            remove_silence=True,
        )

        sf.write(output_path, wav, sr)
        print(f"[TTS LOCAL] Genere en {time.monotonic()-t0:.2f}s -> {output_path}")
        return True

    except Exception as e:
        print(f"[TTS LOCAL] Erreur génération : {e}")
        return False
