import os
import sys
import json
import time

# S'assurer que le dossier racine de JARVIS est dans le path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import module.vector_memory as vector_memory
from module.memory_manager import ajouter_memoire

def populate():
    print("--- POPULATION DE LA MÉMOIRE FACTUELLE (jarvis_memoire.json) ---")
    
    # Ajout des faits clés/valeurs
    faits = {
        "ton café préféré": "Un double espresso serré avec un filet de lait d'avoine.",
        "couleur de ma voiture": "Noir mat satiné avec étriers de freins rouge sport.",
        "mot de passe du wifi": "MylaneJarvisHologram2026!",
        "adresse email principale": "mylane.dev@jarvis.net",
        "sport préféré de mylane": "La boxe anglaise et les séances de HIIT intensives.",
        "heure du réveil idéal": "7h15 pour avoir le temps de courir et coder.",
        "montre préférée": "L'Omega Speedmaster Dark Side of the Moon."
    }
    
    for cle, valeur in faits.items():
        ajouter_memoire(cle, valeur)
        print(f"[OK] Fait ajoute : '{cle}' -> '{valeur}'")
        
    print("\n--- POPULATION DE LA MEMOIRE VECTORIELLE (ChromaDB) ---")
    
    # Ajout d'échanges de conversation riches
    conversations = [
        (
            "Jarvis, je me demande si un jour l'intelligence artificielle aura une conscience.",
            "C'est une question fascinante, mylane. Scientifiquement, nous ne faisons qu'imiter les réseaux neuronaux biologiques, mais l'expérience subjective de la conscience reste le grand mystère de la science."
        ),
        (
            "Qu'est-ce qu'on mange ce soir ? Donne-moi une idée saine et rapide.",
            "Je vous propose un pavé de saumon grillé accompagné de quinoa aux légumes printaniers et d'un filet de citron. Léger, sain et plein d'oméga-3 pour vos séances d'entraînement."
        ),
        (
            "Je suis fatigué en ce moment avec le développement de ton interface holographique.",
            "Prenez soin de vous, mylane. Rome ne s'est pas faite en un jour, et vos algorithmes de réseaux neuronaux 3D tournent déjà à la perfection. Accordez-vous une pause bien méritée."
        ),
        (
            "Jarvis, rappelle-moi pourquoi on a conçu le mode Cortex.",
            "Le mode Cortex a été pensé comme un affichage holographique 3D permettant de visualiser vos souvenirs et faits en temps réel sous forme de constellations synaptiques connectées, offrant une clarté absolue sur ma base de connaissances."
        ),
        (
            "Est-ce que tu penses que la théorie des cordes est valide ?",
            "La théorie des cordes est mathématiquement élégante car elle tente d'unifier la relativité générale et la mécanique quantique dans un espace à 11 dimensions, mais elle manque encore de preuves expérimentales directes."
        ),
        (
            "Comment optimiser le moteur physique de notre carte 3D ?",
            "Pour optimiser le rendu Three.js de la carte domotique, je vous conseille de désactiver le depthWrite sur vos particules transparentes, de regrouper les géométries similaires dans des BufferGeometries, et d'éviter les raycastings à chaque frame."
        ),
        (
            "Quel est ton principal protocole de sécurité en cas d'intrusion ?",
            "En cas d'anomalie réseau détectée, mon protocole isole les sous-systèmes sensibles, chiffre les historiques de conversation en AES-256 et alerte votre terminal principal immédiatement, Monsieur."
        ),
        (
            "Je voudrais partir en week-end à la montagne, tu me conseilles quoi ?",
            "Je vous suggère un séjour à Chamonix, mylane. La météo y est idéale pour les randonnées d'altitude en ce moment, et le chalet de l'Aiguille du Midi dispose d'une connexion d'excellente qualité si vous devez coder."
        )
    ]
    
    for user, assistant in conversations:
        # Utiliser ajouter_souvenir directement
        vector_memory.ajouter_souvenir(user, assistant)
        print(f"[OK] Souvenir vectoriel ajoute : '{user[:40]}...'")
        
    print("\nPopulation de la memoire terminee avec succes !")

if __name__ == "__main__":
    populate()
