"""
competences.py — Système de compétences autonomes de JARVIS.

Génération de plugins Python par LLM (jarvis_creer_competence), suppression
et exécution à chaud. Extrait de main2.py.

send_web_broadcast_sync est un hook injecté par main2.py après import
(évite l'import circulaire).
"""

import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hook remplacé par main2.py après import (envoi d'un payload au HUD web)
def send_web_broadcast_sync(payload):
    pass

# ── ANIMATION VISUELLE & SYSTEME DE COMPETENCES AUTONOMES ─────────────────────

def _effet_visuel_iron_man(stop_event):
    """Affiche un effet de défilement de code et logs style Iron Man HUD dans la console et sur l'écran web."""
    import random
    import time

    # Passer l'orbe en état thinking immédiatement pour l'animer à l'écran
    send_web_broadcast_sync({"action": "set_state", "state": "thinking"})

    logs_fictifs = [
        ">System: Allocating compilation segment on core_0...",
        ">Connecting to Gemini Neural Correlator (Model: gemini-3.5-flash)...",
        ">Enabling thinking mode (Budget: 2048)...",
        ">Synchronizing thought matrix constraints...",
        ">Heap alloc: 0x7ffa4c9e0000 [64mb]",
        "[System] Loading libraries: importlib.util, os, time, sys",
        "[Compile] Generating function signature: def executer(texte_utilisateur=None)",
        "[Parser] Enforcing raw python rules: no markdown tags, pure source...",
        "[Compiler] Building AST Nodes...",
        "[System] Compiling resource: plugins/competence_*.py",
        ">Compacting source code buffer...",
        ">Injecting voice output return strings...",
        ">Shield power stability: 98.4%",
        ">Scanning corrupted sectors... OK",
        "[Log] Dynamic loader thread instantiated.",
        "[Info] Code integrity check: 100% compliant.",
        "[Debug] Temperature: 0.1 | Top-P: 0.95 | Top-K: 40",
    ]
    caracteres = "0123456789ABCDEFghijklmnopqrstuvwxyz[]{}()$#@!*&%^-_=+"

    print("\n\033[93m" + "="*60)
    print("   J.A.R.V.I.S — PLUGINS SYSTEM: COMPILING NEW SKILL")
    print("="*60 + "\033[0m\n")

    iteration = 0
    while not stop_event.is_set():
        val = random.random()
        log_texte = ""
        if val < 0.3:
            log_texte = random.choice(logs_fictifs)
            print(f"\033[94m[HUD_LOG] {log_texte}\033[0m")
        elif val < 0.6:
            addr = f"0x{random.randint(0x10000000, 0xFFFFFFFF):X}"
            data = "".join(random.choice(caracteres) for _ in range(40))
            log_texte = f"{addr} : {data}"
            print(f"\033[92m[MATRICE] {log_texte}\033[0m")
        else:
            progress = random.randint(0, 100)
            bar = "=" * (progress // 5) + " " * (20 - (progress // 5))
            log_texte = f"COMPILING: [{bar}] {progress}%"
            print(f"\033[96m[SYSTEM] {log_texte}\033[0m")
            
        # Toutes les 2 itérations (~80ms), envoyer le log actuel au HUD web pour le défilement
        if iteration % 2 == 0:
            send_web_broadcast_sync({"action": "jarvis_text", "text": f"[HUD] {log_texte}"})
            
        iteration += 1
        time.sleep(0.04)

    print("\n\033[92m" + "="*60)
    print("   J.A.R.V.I.S — SKILL SUCCESSFULLY INTEGRATED")
    print("="*60 + "\033[0m\n")

    # Restaurer l'état d'origine de l'orbe et du texte
    send_web_broadcast_sync({"action": "set_state", "state": "idle"})
    send_web_broadcast_sync({"action": "jarvis_text", "text": "COMPILATION TERMINÉE — COMPÉTENCE CHARGÉE"})


def jarvis_creer_competence(nom_competence: str, description_demande: str) -> str:
    """
    Appelle Gemini-3.5-flash avec thinking activé pour générer une compétence Python autonome.
    Sauvegarde le code généré dans le dossier plugins/ sous competence_<nom>.py.
    """
    import re
    import threading
    import os
    import builtins
    from google.genai import types as _gtypes

    # Valider le client API
    if not hasattr(builtins, "client") or not builtins.client:
        return "Erreur : le client Gemini n'est pas initialisé ou la clé API est invalide."

    nom_formate = re.sub(r'[^a-zA-Z0-9_]', '', nom_competence.lower().replace(" ", "_"))
    dossier_plugins = os.path.join(_BASE_DIR, "plugins")
    if not os.path.exists(dossier_plugins):
        os.makedirs(dossier_plugins, exist_ok=True)
    
    filename = os.path.join(dossier_plugins, f"competence_{nom_formate}.py")

    # Animation Iron Man
    stop_event = threading.Event()
    thread_anim = threading.Thread(target=_effet_visuel_iron_man, args=(stop_event,), daemon=True)
    thread_anim.start()

    try:
        system_instruction = (
            "Tu es l'agent de génération de compétences autonomes de JARVIS.\n"
            "Tu dois écrire du code Python strict, propre et valide.\n\n"
            "RÈGLES CRITIQUES :\n"
            "1. Renvoie UNIQUEMENT le code Python pur. Ne mets AUCUNE balise de code markdown comme ```python ou ```. Pas de texte explicatif en dehors du code.\n"
            "2. Le script doit être entièrement autonome.\n"
            "3. Tu dois obligatoirement implémenter une fonction principale nommée `executer(texte_utilisateur=None)` qui prend un argument optionnel (string) et qui RETOURNE obligatoirement une string (le texte formaté que JARVIS lira à voix haute).\n"
            "4. Évite tout appel externe nécessitant des credentials non fournis (clés d'APIs tierces) à moins que ce ne soit faisable via des APIs publiques ou des mocks. Tu peux utiliser des bibliothèques standards ou requests."
        )

        prompt = (
            f"Génère le code complet pour la compétence : '{nom_competence}'.\n"
            f"Objectif de la compétence : {description_demande}\n\n"
            "Écris le code Python pur respectant toutes les règles de structure."
        )

        # Appel Gemini-3.5-flash avec configuration Thinking
        response = builtins.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=_gtypes.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                thinking_config=_gtypes.ThinkingConfig(thinking_budget=2048)
            )
        )

        code_genere = response.text.strip()
        
        # Nettoyage de sécurité en cas de balises markdown résiduelles
        if code_genere.startswith("```"):
            lines = code_genere.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            code_genere = "\n".join(lines).strip()

        # Écriture du fichier compétence
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_genere)

        stop_event.set()
        thread_anim.join()
        
        print(f"[JARVIS PLUGINS] Nouvelle compétence écrite dans {filename}")
        return f"La compétence '{nom_competence}' a été générée et installée avec succès. Elle est prête à être exécutée."

    except Exception as e:
        stop_event.set()
        thread_anim.join()
        print(f"[JARVIS PLUGINS] Erreur lors de la création de compétence : {e}")
        return f"Désolé Mylane, la génération de la compétence a échoué. Détail de l'erreur : {e}"


def jarvis_supprimer_competence(nom_competence: str) -> str:
    """Supprime proprement le fichier de compétence ciblée."""
    import re
    import os
    nom_formate = re.sub(r'[^a-zA-Z0-9_]', '', nom_competence.lower().replace(" ", "_"))
    filename = os.path.join(_BASE_DIR, "plugins", f"competence_{nom_formate}.py")

    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"[JARVIS PLUGINS] Compétence supprimée : {filename}")
            return f"La compétence '{nom_competence}' a été désinstallée et son fichier a été supprimé."
        except Exception as e:
            return f"Erreur lors de la suppression du fichier : {e}"
    else:
        return f"La compétence '{nom_competence}' n'est pas installée."


def executer_competence_vocale(nom_competence: str, texte_recu: str = None) -> str:
    """Importe et exécute dynamiquement la compétence vocale."""
    import re
    import os
    import sys
    import importlib.util

    nom_formate = re.sub(r'[^a-zA-Z0-9_]', '', nom_competence.lower().replace(" ", "_"))
    filename = os.path.join(_BASE_DIR, "plugins", f"competence_{nom_formate}.py")

    if not os.path.exists(filename):
        return f"Désolé Mylane, la compétence '{nom_competence}' n'est pas disponible."

    try:
        # Importation à chaud
        module_name = f"plugins.competence_{nom_formate}"
        spec = importlib.util.spec_from_file_location(module_name, filename)
        if spec is None or spec.loader is None:
            return "Impossible de charger la spécification du module."

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "executer"):
            res = module.executer(texte_recu)
            return str(res)
        else:
            return "Erreur : cette compétence ne possède pas de point d'entrée 'executer'."

    except Exception as e:
        print(f"[JARVIS PLUGINS] Erreur lors de l'exécution de {nom_competence} : {e}")
        return f"Erreur d'exécution dans la compétence '{nom_competence}' : {e}"


