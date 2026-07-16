import os
import numpy as np

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE_DIR = os.path.join(_BASE_DIR, "core")

# Modèle communautaire openWakeWord pré-entraîné sur "hey jarvis"
WAKEWORD_MODEL_NAME = "hey_jarvis_v0.1"


def init_wakeword():
    """Télécharge le modèle 'hey jarvis' et les modèles de features openWakeWord s'ils sont absents."""
    import openwakeword.utils
    # download_models saute silencieusement les fichiers déjà présents
    openwakeword.utils.download_models(model_names=[WAKEWORD_MODEL_NAME])


class WakeWordDetector:
    """Détecteur de wake word local (openWakeWord, inférence ONNX).

    Usage streaming : appeler le détecteur sur chaque chunk audio int16 16 kHz,
    il retourne le score de détection [0..1] du chunk courant.
    Appeler reset() entre deux phrases pour purger les buffers internes.
    """

    def __init__(self):
        from openwakeword.model import Model
        self.model = Model(
            wakeword_models=[WAKEWORD_MODEL_NAME],
            inference_framework="onnx",
        )

    def __call__(self, audio_chunk_int16) -> float:
        if not isinstance(audio_chunk_int16, np.ndarray):
            audio_chunk_int16 = np.frombuffer(audio_chunk_int16, dtype=np.int16)
        preds = self.model.predict(audio_chunk_int16)
        return max(preds.values()) if preds else 0.0

    def reset(self):
        try:
            self.model.reset()
        except Exception:
            pass
