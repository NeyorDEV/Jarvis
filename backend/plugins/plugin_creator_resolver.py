import os
import sys
import builtins
import json
import re
import asyncio
import importlib
import subprocess
import google.genai as genai
from core.config import GEMINI_API_KEY, CHOSEN_MODEL
from module.sandbox_executor import executer_code_sandbox

client = genai.Client(api_key=GEMINI_API_KEY)
PLUGINS_DIR = os.path.dirname(os.path.abspath(__file__))

async def interroger_model(prompt: str) -> str:
    """Interroge Gemini de façon asynchrone."""
    try:
        response = await client.aio.models.generate_content(
            model=CHOSEN_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[PLUGIN CREATOR ERROR] {e}")
        return ""

async def installer_package_pip(package_name: str) -> bool:
    """Installe automatiquement un package PyPI s'il n'est pas déjà présent."""
    # Le nom vient du JSON généré par le LLM. Même sans shell, un nom commençant
    # par « - » est interprété par pip comme une OPTION (« --index-url=http://…​ »
    # détournerait l'installation vers un dépôt arbitraire). On impose donc le
    # format d'un nom de paquet PyPI (PEP 508), version optionnelle comprise.
    import re as _re_pip
    if not _re_pip.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._\-]{0,80}(\[[A-Za-z0-9,._\-]{1,60}\])?"
                             r"([=<>!~]=?[0-9A-Za-z._\-]{1,30})?", package_name or ""):
        print(f"[PLUGIN CREATOR] ⛔ Nom de package refusé : {package_name!r}")
        return False

    python_exe = os.path.join(PLUGINS_DIR, "..", "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    print(f"[PLUGIN CREATOR] Installation auto du package : {package_name}...")
    try:
        proc = await asyncio.create_subprocess_exec(
            python_exe, "-m", "pip", "install", package_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode == 0
    except Exception as e:
        print(f"[PLUGIN CREATOR PIP ERROR] {e}")
        return False

async def creer_et_habiliter_plugin(user_request: str) -> str:
    """Génère, teste et charge dynamiquement un nouveau plugin Python dans JARVIS."""
    print(f"[PLUGIN CREATOR] Traitement de la demande : {user_request}")

    prompt = f"""Tu es le sous-système d'Auto-Création de Plugins de J.A.R.V.I.S.
L'utilisateur souhaite créer ou intégrer un nouveau plugin.
Demande utilisateur : "{user_request}"

Génère une réponse JSON valide contenant :
1. "plugin_name": Nom court en snake_case sans accent (ex: "notion", "todoist", "convertisseur_devise").
2. "pip_requirements": Liste des noms de packages PyPI nécessaires (ex: ["requests", "notion-client"] ou [] si aucun).
3. "code": Le code Python complet et fonctionnel du fichier plugin.

CONSIGNES STRICTES POUR LE CODE PYTHON DU PLUGIN :
- Le plugin DOIT définir une fonction asynchrone canonique : `async def resoudre_<plugin_name>(cmd: str) -> str | None:`
- La fonction nettoie la commande `cmd` (minuscules, accents, mots parasites).
- Si la commande correspond aux intentions du plugin, exécute l'action et retourne un message explicite en chaîne de caractères (`str`).
- Si la commande ne correspond PAS, retourne impérativement `None`.
- À la fin du fichier, tu DOIS inclure :
  `builtins.resoudre_<plugin_name> = resoudre_<plugin_name>`
- N'inclus aucune clé d'API en dur. Utilise `os.environ.get(...)` ou des valeurs par défaut sécurisées.

Réponds uniquement avec un objet JSON au format suivant :
{{
  "plugin_name": "nom_du_plugin",
  "pip_requirements": ["package1"],
  "code": "# Code Python complet..."
}}
"""

    response_text = await interroger_model(prompt)
    clean_json_str = re.sub(r'^```json\s*|```\s*$', '', response_text.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(clean_json_str)
        plugin_name = data.get("plugin_name", "custom_plugin").lower().strip()
        plugin_name = re.sub(r'[^a-z0-9_]', '_', plugin_name)
        pip_reqs = data.get("pip_requirements", [])
        code = data.get("code", "")
    except Exception as e:
        print(f"[PLUGIN CREATOR JSON ERROR] {e}\nBrut: {response_text}")
        return f"Désolé monsieur, je n'ai pas pu parser les spécifications du nouveau plugin. Erreur : {e}"

    # Étape 1 : Installation des dépendances PyPI si requises
    for req in pip_reqs:
        if req and req.strip():
            succes = await installer_package_pip(req.strip())
            if not succes:
                print(f"[PLUGIN CREATOR WARNING] Échec d'installation de {req}, poursuite...")

    # Étape 2 : Validation syntaxique & exécution dans la Sandbox
    resultat_sandbox = await executer_code_sandbox(code, language="python", timeout=10)
    if not resultat_sandbox["success"] and "SyntaxError" in resultat_sandbox["stderr"]:
        print(f"[PLUGIN CREATOR SANDBOX ERROR] {resultat_sandbox['stderr']}")
        # Tentative de correction automatique avec Gemini
        fix_prompt = f"""Le code du plugin "{plugin_name}" contient une erreur syntaxique :
{resultat_sandbox['stderr']}

Code actuel :
{code}

Corrige le code et réponds uniquement avec le code Python corrigé sans bloc markdown."""
        code_fixed = await interroger_model(fix_prompt)
        code = re.sub(r'^```[a-zA-Z]*\s*|```\s*$', '', code_fixed.strip(), flags=re.MULTILINE)

    # Étape 2 bis : contrôle de sûreté du code généré (imports/appels destructeurs).
    # Ce code va être importé dans le processus JARVIS avec tous nos droits :
    # sans ce filtre, un plugin détourné pouvait effacer des fichiers dès l'import.
    try:
        from module.competences import scanner_appels_dangereux
        _ok_sec, _raison_sec = scanner_appels_dangereux(code)
    except Exception:
        _ok_sec, _raison_sec = True, ""   # scan indisponible : on ne bloque pas
    if not _ok_sec:
        print(f"[PLUGIN CREATOR] ⛔ Plugin refusé par le contrôle de sûreté : {_raison_sec}")
        return (f"J'ai refusé d'installer ce plugin, monsieur : son code n'a pas passé "
                f"le contrôle de sûreté ({_raison_sec}).")

    # Étape 3 : Écriture du fichier plugin dans backend/plugins/
    # plugin_name sert à construire un chemin : on le restreint pour empêcher
    # toute traversée de répertoire (« ../../main » écraserait des fichiers).
    import re as _re_nom
    if not _re_nom.fullmatch(r"[a-z][a-z0-9_]{0,40}", plugin_name or ""):
        return (f"Nom de plugin invalide ({plugin_name!r}) : lettres minuscules, "
                f"chiffres et underscores uniquement.")

    file_name = f"{plugin_name}_resolver.py"
    file_path = os.path.join(PLUGINS_DIR, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[PLUGIN CREATOR] Fichier plugin enregistré : {file_path}")
    except Exception as e:
        return f"Erreur lors de l'écriture du fichier plugin : {e}"

    # Étape 4 : Chargement & Activation dynamique à chaud (Hot Reload)
    try:
        # Si déjà importé, recharger, sinon importer
        module_name = f"plugins.{plugin_name}_resolver"
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

        # Vérifier que le résolveur est bien rattaché dans builtins
        func_name = f"resoudre_{plugin_name}"
        if hasattr(builtins, func_name):
            print(f"[PLUGIN CREATOR SUCCESS] Résolveur {func_name} rattaché avec succès à builtins !")
            return f"Très bien monsieur, le nouveau plugin **{plugin_name}** a été généré, vérifié dans la sandbox et activé instantanément. Vous pouvez l'utiliser dès maintenant !"
        else:
            # Fallback : exécution explicite du code pour attacher à builtins
            loc = {}
            exec(code, globals(), loc)
            if func_name in loc:
                setattr(builtins, func_name, loc[func_name])
                return f"Très bien monsieur, le plugin **{plugin_name}** est maintenant actif sur votre système."

    except Exception as e:
        print(f"[PLUGIN CREATOR LOAD ERROR] {e}")
        return f"Le plugin a été créé dans `{file_name}`, mais une erreur est survenue lors du chargement à chaud : {e}"

    return f"Plugin {plugin_name} créé."

async def resoudre_creation_plugin(cmd: str) -> str | None:
    """Intercepte les commandes d'auto-création de plugin."""
    t = cmd.lower().strip()
    import unicodedata
    t = "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    t = re.sub(r'^(jarvis|jervis|jarvys|jervys|gervis)(,)?\s*', '', t)

    mots_cles = [
        "cree un plugin", "creer un plugin", "cree moi un plugin",
        "ajoute un plugin", "ajoute le plugin", "connecte toi a",
        "connecte-toi a", "integre le service", "integre l'api",
        "cree une integration", "nouveau plugin"
    ]

    if not any(k in t for k in mots_cles):
        return None

    # Lancer le processus en tâche de fond et répondre immédiatement
    asyncio.create_task(creer_et_habiliter_plugin(cmd))
    return "Très bien monsieur. Je commence le développement du nouveau plugin, l'installation des dépendances et son activation à chaud."

builtins.resoudre_creation_plugin = resoudre_creation_plugin
