import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
import module.vector_memory as vector_memory

def afficher_tout():
    print("\n" + "="*50)
    print("       HISTORIQUE PROFOND DE JARVIS (Vector DB)")
    print("="*50 + "\n")
    
    souvenirs = vector_memory.lister_souvenirs()
    
    if not souvenirs:
        print("La mémoire est actuellement vide.")
    else:
        for i, s in enumerate(souvenirs, 1):
            print(f"SOUVENIR #{i}")
            print(s)
            print("-" * 30)
            
    print(f"\nTotal : {len(souvenirs)} souvenir(s) enregistré(s).")
    input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    afficher_tout()
