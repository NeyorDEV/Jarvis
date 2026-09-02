import os
import re
import requests
from urllib.parse import urlparse
from typing import Optional, Tuple, List, Dict, Any
class JarvisLocalAgentManager:
    """
    Gestionnaire pour l'agent local basé sur Ollama.
    Permet une intégration optionnelle (opt-in), privée et gratuite dans JARVIS.
    """
    def __init__(self, model_name=None):
        self.base_url: str = os.environ.get("JARVIS_OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.model: str = model_name if model_name else os.environ.get("JARVIS_OLLAMA_MODEL", "llama3")
    def _get_ollama_tags_url(self) -> str:
        parsed = urlparse(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}/api/tags"
    def check_system(self) -> Tuple[bool, str]:
        """Vérifie rapidement si Ollama tourne et si le modèle requis est disponible."""
        api_url = self._get_ollama_tags_url()
        try:
            response = requests.get(api_url, timeout=3.0)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return False, "OLLAMA_NOT_RUNNING"
        try:
            data = response.json()
            models = [m.get("name") for m in data.get("models", [])]
            model_found = False
            for m in models:
                if m == self.model or m == f"{self.model}:latest" or self.model == m + ":latest":
                    model_found = True
                    break
            if not model_found:
                return False, "MODEL_NOT_PULLED"
        except ValueError:
            return False, "INVALID_RESPONSE"
        return True, "OK"
    def clean_thinking(self, text: str, strip_thinking: bool = True) -> str:
        """Supprime les balises <think>...</think> des modèles comme DeepSeek."""
        if not text:
            return ""
        if strip_thinking:
            cleaned = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
            cleaned = cleaned.replace("<think>", "").replace("</think>", "")
            return cleaned.strip()
        return text.strip()
    def generate_response(self, prompt: str) -> Optional[str]:
        """Appelle l'agent local Ollama."""
        is_ok, status = self.check_system()
        if not is_ok:
            print(f"[OLLAMA LOCAL] Impossible d'appeler l'agent local : status={status}")
            return None
        try:
            parsed = urlparse(self.base_url)
            api_url = f"{parsed.scheme}://{parsed.netloc}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_ctx": 16384
                }
            }
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            raw_text = data.get("response", "")
            return self.clean_thinking(raw_text)
        except Exception as e:
            print(f"[OLLAMA LOCAL ERROR] : {e}")
            return None