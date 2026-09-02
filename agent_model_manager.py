import builtins
import json
import os
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jarvis_model_config.json")
# Dictionnaire des modeles disponibles par agent / categorie
AVAILABLE_MODELS = {
    "Gemini": [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-pro",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash"
    ],
    "Grok": [
        "grok-beta",
        "grok-2-1212",
        "grok-4.5",
        "grok-4.3"
    ],
    "Claude": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-latest",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ],
    "Groq": [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b"
    ],
    "ChatGPT": [
        "gpt-4o",
        "gpt-4o-mini",
        "o3-mini"
    ],
    "Ollama (Local)": [
        "llama3",
        "mistral",
        "qwen2.5-coder:7b",
        "deepseek-coder-v2"
    ]
}
DEFAULT_MODELS = {
    "PM": "gemini-2.5-flash",
    "UI": "gemini-2.5-flash",
    "DEV": "gemini-2.5-pro",
    "SEC": "gemini-2.5-flash",
    "QA": "gemini-2.5-flash",
    "OPS": "gemini-2.5-flash"
}
def load_chosen_models():
    """Charge les modeles preferes depuis le JSON ou retourne les defauts."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                loaded_models = config.get("chosen_models", {})
                result = DEFAULT_MODELS.copy()
                for agent, model in loaded_models.items():
                    result[agent] = model
                return result
    except Exception as e:
        print(f"[AGENT MODEL MANAGER] Erreur chargement : {e}")
    return DEFAULT_MODELS.copy()
def save_chosen_models(models_dict):
    """Sauvegarde le dictionnaire de modeles choisis dans le JSON."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"chosen_models": models_dict}, f, indent=2)
        print(f"[AGENT MODEL MANAGER] Configuration sauvegardée dans {CONFIG_PATH}")
    except Exception as e:
        print(f"[AGENT MODEL MANAGER] Erreur sauvegarde : {e}")
def get_agent_models_info():
    """Retourne la structure complete pour l'interface web."""
    current = load_chosen_models()
    return {
        "available_models": AVAILABLE_MODELS,
        "current_models": current
    }
def set_agent_models(new_models_dict):
    """Met a jour et sauvegarde les modeles."""
    current = load_chosen_models()
    for agent, model in new_models_dict.items():
        current[agent] = model
    builtins.CHOSEN_MODELS = current
    save_chosen_models(current)
    return current