import os
import sys
import asyncio

# Ajout du chemin du backend dans le sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from backend.module.website_builder import telecharger_image_ia, generer_site_web_autonome

async def test_website_builder():
    print("[TEST] Démarrage des tests unitaires du Website Builder...")
    
    # Test 1 : Génération et téléchargement d'image IA
    test_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_assets", "test_hero.jpg"))
    print(f"[TEST 1] Test de génération d'image IA vers {test_img_path}...")
    success = telecharger_image_ia("Futuristic AI cybernetic neural core 4k", test_img_path)
    assert success, "La génération ou le fallback d'image doit réussir"
    assert os.path.exists(test_img_path) or os.path.exists(test_img_path.rsplit('.', 1)[0] + ".svg"), "Le fichier image doit exister"
    print("[TEST 1 PASSED] Image générée avec succès !")

    # Nettoyage
    if os.path.exists(test_img_path):
        os.remove(test_img_path)

    print("[TEST] Tous les tests de base sont validés avec succès !")

if __name__ == "__main__":
    asyncio.run(test_website_builder())
