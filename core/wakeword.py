import os
import numpy as np

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE_DIR = os.path.join(_BASE_DIR, "core")

# Modèle communautaire openWakeWord pré-entraîné sur "hey jarvis"
WAKEWORD_MODEL_NAME = "hey_jarvis_v0.1"

# Modèle custom entraîné sur "jarvis" prononcé à la française
# (voir training/wakeword/jarvis_fr_colab.ipynb). S'il existe, il est
# utilisé automatiquement à la place de hey_jarvis.
CUSTOM_MODEL_PATH = os.path.join(_CORE_DIR, "jarvis_fr.onnx")


def init_wakeword():
    """Télécharge le modèle 'hey jarvis' et les modèles de features openWakeWord s'ils sont absents."""
    import openwakeword.utils
    # download_models saute silencieusement les fichiers déjà présents
    # (les modèles de features melspectrogram/embedding sont requis même avec un modèle custom)
    openwakeword.utils.download_models(model_names=[WAKEWORD_MODEL_NAME])


class WakeWordDetector:
    """Détecteur de wake word local (openWakeWord, inférence ONNX).

    Usage streaming : appeler le détecteur sur chaque chunk audio int16 16 kHz,
    il retourne le score de détection [0..1] du chunk courant.
    Appeler reset() entre deux phrases pour purger les buffers internes.
    """

    def __init__(self):
        from openwakeword.model import Model
        if os.path.exists(CUSTOM_MODEL_PATH):
            modele = CUSTOM_MODEL_PATH
            print(f"🎙  [WAKEWORD] Modèle custom français détecté : {os.path.basename(CUSTOM_MODEL_PATH)}")
        else:
            modele = WAKEWORD_MODEL_NAME
        self.model = Model(
            wakeword_models=[modele],
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
