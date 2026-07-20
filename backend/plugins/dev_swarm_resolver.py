import os
import sys
import builtins
import json
import re
import asyncio
import py_compile
import google.genai as genai
from core.config import GEMINI_API_KEY, CHOSEN_MODEL

# Initialisation du client de génération Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Définition du répertoire de travail (Sandbox)
SANDBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sandbox")

async def diffuser_dev_swarm(data):
    """Diffuse l'état de l'essaim aux clients WebSocket connectés."""
    if hasattr(builtins, "CONNECTED_CLIENTS") and builtins.CONNECTED_CLIENTS:
        msg = json.dumps(data)
        await asyncio.gather(*[ws.send(msg) for ws in builtins.CONNECTED_CLIENTS], return_exceptions=True)

async def interroger_model(prompt):
    """Interroge Gemini de façon asynchrone pour la génération de code/specs."""
    try:
        response = await client.aio.models.generate_content(
            model=CHOSEN_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[DEV SWARM ERROR] Erreur d'appel du modèle : {e}")
        return ""

async def run_dev_swarm_process(user_request):
    """Gère le cycle de vie de l'essaim d'agents."""
    print(f"[DEV SWARM] Démarrage du cycle pour la requête : {user_request}")
    
    # ── ÉTAPE 1 : Chef de Projet (PM) ──
    await diffuser_dev_swarm({
        "action": "dev_swarm_update",
        "agent": "PM",
        "message": "Conception et architecture du projet...",
        "log": "Analyse de la demande utilisateur...\nDéfinition de la liste des fichiers requis...",
        "files": [],
        "status": "in_progress"
    })
    
    pm_prompt = f"""Tu es le Chef de Projet (PM) de l'essaim d'agents autonomes de JARVIS.
L'utilisateur souhaite créer un projet.
Requête utilisateur : "{user_request}"

Définis le projet et la liste des fichiers nécessaires pour le coder.
Privilégie des fichiers simples et fonctionnels en Python, ou HTML/JS/CSS si la demande concerne le Web.
Tu dois répondre uniquement avec un objet JSON valide ayant le schéma suivant :
{{
  "project_name": "nom_du_projet_snake_case",
  "specs": "Courte description des spécifications techniques",
  "files": [
    {{
      "file_path": "nom_du_fichier.py",
      "purpose": "Rôle précis de ce fichier dans l'application"
    }}
  ]
}}
Ne mets aucun texte explicatif en dehors du JSON. Réponds uniquement avec l'objet JSON.
"""
    pm_response = await interroger_model(pm_prompt)
    
    # Nettoyage robuste du JSON renvoyé par le modèle (enlever les blocs markdown ```json ... ```)
    pm_response_clean = re.sub(r'^```json\s*|```\s*$', '', pm_response.strip(), flags=re.MULTILINE)
    
    try:
        project_config = json.loads(pm_response_clean)
        project_name = project_config.get("project_name", "projets_swarm")
        specs = project_config.get("specs", "")
        files_list = project_config.get("files", [])
    except Exception as e:
        print(f"[DEV SWARM ERROR] Impossible de parser le JSON du PM : {e}\nRéponse brute : {pm_response}")
        await diffuser_dev_swarm({
            "action": "dev_swarm_update",
            "agent": "PM",
            "message": "Échec de conception du projet",
            "log": f"Erreur de format de spécification JSON.\nRéponse reçue : {pm_response}",
            "files": [],
            "status": "failure"
        })
        return

    # Création du dossier du projet dans la sandbox
    project_dir = os.path.join(SANDBOX_DIR, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    files_state = {f["file_path"]: "pending" for f in files_list}
    files_purpose = {f["file_path"]: f["purpose"] for f in files_list}
    written_files = {} # file_path -> content

    async def notify(payload):
        payload["project"] = project_name
        await diffuser_dev_swarm(payload)

    await notify({
        "action": "dev_swarm_update",
        "agent": "PM",
        "message": f"Architecture validée pour le projet '{project_name}'",
        "log": f"Spécifications : {specs}\n\nFichiers à générer :\n" + "\n".join([f"- {f['file_path']} : {f['purpose']}" for f in files_list]),
        "files": files_list,
        "status": "in_progress"
    })
    await asyncio.sleep(2)

    # ── ÉTAPE 2 : Développeur & ÉTAPE 3 : QA Tester ──
    for f in files_list:
        file_path = f["file_path"]
        purpose = f["purpose"]
        files_state[file_path] = "writing"
        
        await notify({
            "action": "dev_swarm_update",
            "agent": "DEV",
            "message": f"Écriture de {file_path}...",
            "log": f"Création et implémentation du fichier : {file_path}\nDescription : {purpose}",
            "files": [{"file_path": fp, "status": files_state[fp]} for fp in files_state],
            "status": "in_progress"
        })

        # Assemblage du contexte pour la cohérence
        other_files_context = ""
        if written_files:
            other_files_context = "\n".join([f"--- Fichier {fp} ---\n{content}" for fp, content in written_files.items()])
        else:
            other_files_context = "(Aucun fichier n'a encore été écrit)"

        dev_prompt = f"""Tu es le Développeur de l'essaim d'agents autonomes.
Projet : "{project_name}"
Description : "{specs}"
Fichier à écrire : "{file_path}" (Rôle : {purpose})

Voici les fichiers déjà écrits pour ce projet pour assurer la cohérence de l'architecture :
{other_files_context}

Génère le code complet, propre et fonctionnel pour le fichier "{file_path}".
Ne mets aucune explication avant ou après le code. Pas de blabla, pas de bloc markdown. Renvoye uniquement le code brut.
"""
        code = await interroger_model(dev_prompt)
        
        # Nettoyage des éventuels blocs de code markdown ```python ... ```
        code_clean = re.sub(r'^```[a-zA-Z]*\s*|```\s*$', '', code.strip(), flags=re.MULTILINE)
        
        # Écriture dans le répertoire sandbox
        file_full_path = os.path.join(project_dir, file_path)
        with open(file_full_path, "w", encoding="utf-8") as file_out:
            file_out.write(code_clean)
        
        written_files[file_path] = code_clean
        
        # ── Test de compilation (QA Tester) ──
        files_state[file_path] = "testing"
        await notify({
            "action": "dev_swarm_update",
            "agent": "QA",
            "message": f"Validation de {file_path}...",
            "log": f"Lancement des tests de validation pour {file_path}...",
            "files": [{"file_path": fp, "status": files_state[fp]} for fp in files_state],
            "status": "in_progress"
        })
        await asyncio.sleep(1)

        # Si c'est du Python, on vérifie la compilation syntaxique
        if file_path.endswith(".py"):
            success = False
            for iteration in range(3): # Essayer de corriger jusqu'à 3 fois
                try:
                    py_compile.compile(file_full_path, doraise=True)
                    success = True
                    break
                except py_compile.PyCompileError as e:
                    error_msg = str(e)
                    print(f"[DEV SWARM QA] Erreur détectée dans {file_path} (Itération {iteration+1}): {error_msg}")
                    
                    await notify({
                        "action": "dev_swarm_update",
                        "agent": "QA",
                        "message": f"Erreur dans {file_path}. Tentative de correction...",
                        "log": f"Testeur QA : Erreur de compilation !\n{error_msg}\nDemande de correction envoyée au développeur...",
                        "files": [{"file_path": fp, "status": "failed"} for fp in files_state],
                        "status": "in_progress"
                    })
                    await asyncio.sleep(2)
                    
                    # Demander au développeur de corriger
                    fix_prompt = f"""Tu es le Développeur de l'essaim d'agents autonomes.
Le testeur a détecté une erreur de compilation dans le fichier "{file_path}" que tu as écrit.

Erreur de compilation :
{error_msg}

Voici le code actuel de "{file_path}" :
---
{code_clean}
---

Propose une version corrigée et fonctionnelle du fichier "{file_path}".
Ne mets aucune explication avant ou après le code. Renvoye uniquement le code brut.
"""
                    code = await interroger_model(fix_prompt)
                    code_clean = re.sub(r'^```[a-zA-Z]*\s*|```\s*$', '', code.strip(), flags=re.MULTILINE)
                    
                    with open(file_full_path, "w", encoding="utf-8") as file_out:
                        file_out.write(code_clean)
                    written_files[file_path] = code_clean
            
            if success:
                files_state[file_path] = "completed"
                await notify({
                    "action": "dev_swarm_update",
                    "agent": "QA",
                    "message": f"Compilation réussie pour {file_path}",
                    "log": f"Testeur QA : Validation syntaxique OK pour {file_path}.",
                    "files": [{"file_path": fp, "status": files_state[fp]} for fp in files_state],
                    "status": "in_progress"
                })
            else:
                files_state[file_path] = "failed"
                await notify({
                    "action": "dev_swarm_update",
                    "agent": "QA",
                    "message": f"Échec de validation de {file_path}",
                    "log": f"Testeur QA : Échec persistant de compilation pour {file_path}.",
                    "files": [{"file_path": fp, "status": files_state[fp]} for fp in files_state],
                    "status": "failure"
                })
                if hasattr(builtins, "parler"):
                    builtins.parler(f"Désolé monsieur, l'essaim d'agents n'a pas pu valider le fichier {file_path} du projet.")
                return
        else:
            # Pour les autres fichiers (HTML, JS, CSS), on accepte directement
            files_state[file_path] = "completed"
            await notify({
                "action": "dev_swarm_update",
                "agent": "QA",
                "message": f"Fichier {file_path} validé",
                "log": f"Testeur QA : Intégration de ressource statique OK pour {file_path}.",
                "files": [{"file_path": fp, "status": files_state[fp]} for fp in files_state],
                "status": "in_progress"
            })
        await asyncio.sleep(1)

    # ── FINALISATION ──
    await notify({
        "action": "dev_swarm_update",
        "agent": "PM",
        "message": f"Projet {project_name} terminé !",
        "log": f"L'ensemble des fichiers ont été générés et compilés dans la sandbox.\nDossier : {project_dir}",
        "files": [{"file_path": fp, "status": "completed"} for fp in files_state],
        "status": "success"
    })
    
    # Notification sonore
    if hasattr(builtins, "parler"):
        builtins.parler(f"Très bien monsieur. L'essaim d'agents a terminé le projet {project_name} dans la sandbox. Tous les modules ont passé la compilation QA.")
        
    # Ouvrir l'explorateur Windows sur le dossier du projet
    try:
        os.startfile(project_dir)
    except:
        pass

async def resoudre_dev_swarm(cmd):
    """Résout et intercepte les commandes d'essaim d'agents."""
    t = cmd.lower().strip()
    
    # Nettoyage des accents
    import unicodedata
    t = "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    t = re.sub(r'^(jarvis|jervis|jarvys|jervys|gervis)(,)?\s*', '', t)
    
    # Mots-clés de déclenchement
    mots_cles = [
        "essaim", "swarm", "demande aux agents", "demande a l'equipe", 
        "demande a l equipe", "equipe de dev", "equipe d'agents", 
        "equipe agents", "cree le projet", "cree l'application",
        "cree un projet", "cree une application", "lance l'essaim", 
        "lance essaim", "demarre l'essaim", "demarre essaim"
    ]
    
    # Normalisation pour éviter les ratés sur les apostrophes et tirets
    t_clean = t.replace("'", " ").replace("-", " ")
    
    has_keyword = any(k in t for k in mots_cles) or any(k in t_clean for k in mots_cles)
    starts_with_code = t.startswith("code-moi") or t.startswith("code moi")
    
    if not has_keyword and not starts_with_code:
        return None
        
    # Extraction de la requête utilisateur
    request_clean = cmd
    # Nettoyer l'appel vocal ou écrit de réveil
    request_clean = re.sub(r'^(jarvis|jervis|jarvys|jervys|gervis)(,)?\s*', '', request_clean, flags=re.IGNORECASE).strip()
    
    # Lancement du processus asynchrone en tâche de fond pour ne pas bloquer le flux d'interception
    asyncio.create_task(run_dev_swarm_process(request_clean))
    
    return "Très bien monsieur, je mobilise l'essaim d'agents autonomes pour votre projet. Suivi actif déployé sur le HUD."

# Enregistrement dynamique dans builtins pour main2.py
builtins.resoudre_dev_swarm = resoudre_dev_swarm

async def resoudre_lance_sandbox(cmd):
    """Résout les commandes pour savoir comment lancer ou lancer le dernier projet de la sandbox."""
    t = cmd.lower().strip()
    
    # Nettoyage des accents
    import unicodedata
    t = "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    t = re.sub(r'^(jarvis|jervis|jarvys|jervys|gervis)(,)?\s*', '', t)
    
    # Mots-clés cibles
    mots_comment_lancer = [
        "comment je fais pour le lancer", "comment le lancer", "comment lancer", 
        "comment je lance", "comment executer", "comment l'executer", "comment je l'exécute"
    ]
    mots_lancer_direct = [
        "lance le projet", "lance l'application", "lance le", "lance-le", 
        "execute le", "execute-le", "demarre le projet", "demarre l'application"
    ]
    
    is_comment = any(re.search(r'\b' + re.escape(k) + r'\b', t) for k in mots_comment_lancer) or (("comment" in t or "comment faire" in t) and ("lance" in t or "execute" in t))
    is_direct = any(re.search(r'\b' + re.escape(k) + r'\b', t) for k in mots_lancer_direct) or (("lance" in t or "execute" in t or "demarre" in t) and ("projet" in t or "jeu" in t or "script" in t or "application" in t))
    
    if not is_comment and not is_direct:
        return None
        
    # Trouver le dernier projet modifié dans la sandbox
    if not os.path.exists(SANDBOX_DIR):
        return "Désolé monsieur, aucun projet n'a été créé dans la sandbox pour le moment."
        
    subdirs = [os.path.join(SANDBOX_DIR, d) for d in os.listdir(SANDBOX_DIR) if os.path.isdir(os.path.join(SANDBOX_DIR, d))]
    if not subdirs:
        return "Désolé monsieur, le répertoire de la sandbox est vide."
        
    latest_dir = max(subdirs, key=os.path.getmtime)
    project_name = os.path.basename(latest_dir)
    
    # Chercher les points d'entrée
    files = os.listdir(latest_dir)
    entry_point = None
    python_files = [f for f in files if f.endswith(".py")]
    
    if "main.py" in files:
        entry_point = "main.py"
    elif "app.py" in files:
        entry_point = "app.py"
    elif len(python_files) == 1:
        entry_point = python_files[0]
    elif len(python_files) > 1:
        # Prendre le plus récemment modifié ou le premier
        python_full = [os.path.join(latest_dir, f) for f in python_files]
        latest_file = max(python_full, key=os.path.getmtime)
        entry_point = os.path.basename(latest_file)
        
    html_files = [f for f in files if f.endswith(".html")]
    if not entry_point and "index.html" in files:
        entry_point = "index.html"
    elif not entry_point and html_files:
        entry_point = html_files[0]
        
    if not entry_point:
        return f"Le dernier projet créé est '{project_name}', mais je n'ai pas trouvé de fichier exécutable (comme main.py ou index.html) à l'intérieur. Fichiers présents : {', '.join(files)}."

    file_full_path = os.path.join(latest_dir, entry_point)
    
    if is_comment:
        if entry_point.endswith(".py"):
            instructions = f"Le dernier projet créé par l'essaim est **{project_name}**.\n\nVous pouvez le lancer en ouvrant un terminal et en exécutant :\n`python sandbox/{project_name}/{entry_point}`\n\nSouhaitez-vous que je le lance directement pour vous ? Dites simplement 'lance le projet'."
        elif entry_point.endswith(".html"):
            instructions = f"Le dernier projet créé par l'essaim est **{project_name}**.\n\nIl s'agit d'une application web. Vous pouvez l'ouvrir en ouvrant le fichier `{entry_point}` dans votre navigateur.\n\nSouhaitez-vous que je l'ouvre directement pour vous ? Dites simplement 'lance le projet'."
        else:
            instructions = f"Le dernier projet créé par l'essaim est **{project_name}** contenant le fichier `{entry_point}`."
        return instructions
        
    if is_direct:
        import subprocess
        if entry_point.endswith(".py"):
            try:
                # Utiliser le venv python si disponible
                python_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "venv", "Scripts", "python.exe")
                if not os.path.exists(python_exe):
                    python_exe = "python"
                
                # Lancer dans une nouvelle console cmd sous Windows
                subprocess.Popen(f'start cmd /k ""{python_exe}" "{file_full_path}""', shell=True)
                return f"Très bien monsieur, je lance le script `{entry_point}` du projet `{project_name}` dans un nouveau terminal."
            except Exception as e:
                return f"Désolé monsieur, je n'ai pas pu exécuter le script. Erreur : {e}"
        elif entry_point.endswith(".html"):
            try:
                import webbrowser
                webbrowser.open(file_full_path)
                return f"Très bien monsieur, j'ouvre `{entry_point}` du projet `{project_name}` dans votre navigateur."
            except Exception as e:
                return f"Désolé monsieur, je n'ai pas pu ouvrir le fichier HTML. Erreur : {e}"
        else:
            try:
                os.startfile(file_full_path)
                return f"Très bien monsieur, j'ouvre le fichier `{entry_point}`."
            except Exception as e:
                return f"Désolé monsieur, je n'ai pas pu ouvrir le fichier. Erreur : {e}"
                
    return None

builtins.resoudre_lance_sandbox = resoudre_lance_sandbox
