import re
import json

path = r"N:\JARVIS\JARVIS_Commandes.txt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

commands = []
for line in content.splitlines():
    line = line.strip()
    # Check if it is a command line starting with '- '
    if line.startswith("- "):
        # Remove the leading '- '
        cmd_part = line[2:]
        # Split on '->' to get only the trigger phrases
        if "->" in cmd_part:
            cmd_part = cmd_part.split("->")[0].strip()
        
        # Split on '/' to get individual variants
        parts = [p.strip() for p in cmd_part.split("/")]
        
        for p in parts:
            # Clean up bracket syntax [A / B / C] into individual clean examples, or keep simple illustrative forms
            p = p.strip()
            if not p:
                continue
            # Remove trailing '?' or punctuation, but keep typical formats
            # Let's clean bracket placeholders for simple representation
            # e.g. "Ouvre le dossier [Nom]" -> "Ouvre le dossier Bureau" or "Ouvre le dossier Documents"
            # We can expand them or keep them as clean text strings
            if "[" in p and "]" in p:
                # If it's a simple placeholder, replace it with a typical value
                p = p.replace("[X]", "10")
                p = p.replace("[x]", "10")
                p = p.replace("[Nom]", "Documents")
                p = p.replace("[Ancien]", "ancien_dossier")
                p = p.replace("[Nouveau]", "nouveau_dossier")
                p = p.replace("[Fichier]", "photo.jpg")
                p = p.replace("[Destination]", "Images")
                p = p.replace("[Calculatrice / Notepad / Paint / Chrome / Firefox / Edge / Opera]", "Calculatrice")
                p = p.replace("[Steam / Origin / EA App / Gestionnaire de tâches]", "Steam")
                p = p.replace("[Nom de l'application]", "Calculatrice")
                p = p.replace("[Calendrier / Météo / Musique]", "Météo")
                p = p.replace("[Lieu/Ville/Pays]", "Tokyo")
                p = p.replace("[Nom de Lieu]", "Paris")
                p = p.replace("[Ville A]", "Paris")
                p = p.replace("[Ville B]", "Lyon")
                p = p.replace("[A]", "Paris")
                p = p.replace("[B]", "Lyon")
                p = p.replace("[Netflix / YouTube / Disney+ / Prime Video / Deezer / Crunchyroll / Twitch / Apple TV]", "Netflix")
                p = p.replace("[Titre]", "Billie Jean")
                p = p.replace("[Artiste]", "Michael Jackson")
                p = p.replace("[Artiste/Sujet]", "Michael Jackson")
                p = p.replace("[Titre/Artiste]", "Billie Jean")
                p = p.replace("[Titre / Artiste]", "Billie Jean")
                p = p.replace("[URL]", "google.fr")
                p = p.replace("[Texte]", "Bonjour")
                p = p.replace("[Sélecteur/Champ]", "champ de recherche")
                p = p.replace("[Bouton]", "Rechercher")
                p = p.replace("[Nom de la scène]", "Cinéma")
                p = p.replace("[Description]", "un coucher de soleil")
                p = p.replace("[Information]", "mon mot de passe est secret")
                p = p.replace("[Info]", "mon mot de passe est secret")
                p = p.replace("[Sujet]", "musique")
                p = p.replace("[Email]", "mylane@example.com")
                p = p.replace("[Corps]", "Salut comment ça va ?")
                p = p.replace("[Date début]", "demain à 10 heures")
                p = p.replace("[Date fin]", "demain à 11 heures")
                p = p.replace("[Chemin local]", "C:\\photo.jpg")
                p = p.replace("[Élément]", "du café")
                p = p.replace("[Tâche]", "faire la vaisselle")
                p = p.replace("[Tache]", "faire la vaisselle")
                p = p.replace("[Heure]", "18 heures")
                p = p.replace("[Langue]", "anglais")
                p = p.replace("[Mot]", "bonjour")
                p = p.replace("[Nom du Contact]", "Julie")
                p = p.replace("[à X faces]", "à 6 faces")
                p = p.replace("[de X caractères]", "de 12 caractères")
                p = p.replace("[Pays]", "France")
                p = p.replace("[Ville]", "Tokyo")
                p = p.replace("[nom]", "recherche_web")
                p = p.replace("[description]", "faire des recherches")
                p = p.replace("[avec paramètre]", "avec python")
                p = p.replace("[débutant (600 Elo) / novice (800 Elo) / moyen (1000 Elo) / intermédiaire (1400 Elo) / expert (1800 Elo) / maître (2000 Elo)]", "moyen")
                p = p.replace("[blancs / noirs]", "blancs")
                p = p.replace("[avec / sans]", "avec")
                p = p.replace("[blancs/noirs]", "blancs")
                p = p.replace("[facile/moyen/difficile]", "moyen")
                p = p.replace("[avec/sans]", "avec")
                p = p.replace("[Salon / Chambre / Bureau / Cuisine]", "Salon")
                p = p.replace("[Couleur]", "Bleu")
                p = p.replace("[Bureau / Sapin / ...]", "Bureau")
                p = p.replace("[Salon / Bureau]", "Salon")
                p = p.replace("[Bureau]", "Bureau")
                p = p.replace("[Mon téléphone / Téléphone de Julie / ...]", "mon téléphone")
                p = p.replace("[Appareil]", "la télévision")
                
            # Clean double quotes and weird formatting
            p = p.strip()
            # If line is just a bullet or stars, skip
            if not p or p.startswith("*") or p.endswith("*"):
                continue
            
            # De-duplicate case insensitively
            if p.lower() not in [c.lower() for c in commands]:
                commands.append(p)

print(json.dumps(commands, ensure_ascii=False, indent=2))
