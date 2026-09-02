"""
core/stt.py
───────────
Speech-To-Text : transcription audio via Groq Whisper + fallback Google STT.
Extrait de main2.py (lignes 3967-4053).

Export principal :
    transcribe_audio_groq(raw_bytes, sample_rate, recognizer, groq_client,
                          wake_word, jarvis_actif) → str | None
"""

import os
import tempfile
import wave


# Hallucinations Whisper connues à filtrer
_WHISPER_HALLUCINATIONS = frozenset({
    "merci", "merci beaucoup", "merci à tous", "je vous remercie",
    "bonjour", "you", "thank you", "subtitles", "sous-titres",
    "sous-titres par amara.org", "sous-titres réalisés par la communauté d'amara.org",
    "subtitles by amara.org",
    "sous-titrage société radio-canada", "sous-titrage société radio canada",
    "sous-titres société radio-canada", "sous-titres société radio canada",
    "sous-titres par la société radio-canada", "société radio-canada", "radio-canada",
    "sous-titrage st' 501", "sous-titrage st 501", "sous-titres st' 501", "sous-titres st 501",
    "sous-titrage", "sous-titres par",
})


def transcribe_audio_groq(
    raw_audio_bytes: bytes,
    sample_rate: int = 16000,
    recognizer=None,
    groq_client=None,
    wake_word: str = "jarvis",
    jarvis_actif: bool = False,
) -> str | None:
    """
    Transcrit un segment audio brut (PCM 16-bit mono).

    Stratégie :
      1. Groq Whisper (ultra-rapide, ~150ms) si groq_client fourni
      2. Google STT (fallback fiable) si recognizer fourni

    Args:
        raw_audio_bytes: bytes PCM bruts (int16, mono)
        sample_rate:     fréquence d'échantillonnage (défaut 16000)
        recognizer:      instance sr.Recognizer pour le fallback Google
        groq_client:     client Groq initialisé (ou None)
        wake_word:       mot de réveil (pour les logs conditionnels)
        jarvis_actif:    True si la session est active (pour les logs)

    Returns:
        Texte transcrit en minuscules, ou None si échec total.
    """
    import time

    # ── Tentative 1 : Groq Whisper ────────────────────────────────────────────
    if groq_client:
        try:
            import io
            t0 = time.time()
            audio_buffer = io.BytesIO()
            
            with wave.open(audio_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)   # 16-bit = 2 bytes
                wf.setframerate(sample_rate)
                wf.writeframes(raw_audio_bytes)
            
            audio_buffer.seek(0)
            transcription = groq_client.audio.transcriptions.create(
                file=("audio.wav", audio_buffer.read()),
                model="whisper-large-v3-turbo",
                language="fr",
                response_format="text",
            )

            elapsed = time.time() - t0
            texte = (
                transcription.strip().lower()
                if isinstance(transcription, str)
                else str(transcription).strip().lower()
            )

            # Filtrer les hallucinations sur le silence/bruit
            texte_clean = texte.rstrip(".!? ")
            if texte_clean in _WHISPER_HALLUCINATIONS:
                if jarvis_actif or (wake_word in texte):
                    print(f"[STT] Groq Whisper : Hallucination détectée ('{texte}'), repli Google.")
                return None

            if texte and len(texte) > 1:
                if jarvis_actif or (wake_word in texte):
                    print(f"[STT] Groq Whisper OK ({elapsed:.2f}s) : {texte}")
                return texte
            else:
                if jarvis_actif:
                    print("[STT] Groq Whisper : réponse vide, fallback Google.")

        except Exception as e:
            if jarvis_actif:
                print(f"[STT] Groq Whisper erreur : {e} — fallback Google.")

    # ── Tentative 2 : Google STT ──────────────────────────────────────────────
    if recognizer:
        try:
            import speech_recognition as sr
            audio_data = sr.AudioData(raw_audio_bytes, sample_rate, 2)
            texte = recognizer.recognize_google(audio_data, language="fr-FR").lower().strip()
            if texte:
                if jarvis_actif or (wake_word in texte):
                    print(f"[STT] Google STT (fallback) : {texte}")
                return texte
        except Exception as e:
            if hasattr(e, "__class__") and e.__class__.__name__ == "UnknownValueError":
                pass  # Silence ou parole non reconnue
            else:
                print(f"[STT] Google STT erreur : {e}")

    return None
