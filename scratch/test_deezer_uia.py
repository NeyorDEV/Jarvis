import sys
import os
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

try:
    import uiautomation as auto
except Exception as e:
    print(f"❌ Impossible d'importer uiautomation : {e}")
    sys.exit(1)

def print_element_tree(control, depth=0, max_depth=3):
    """Parcourt et affiche récursivement l'arbre d'UI Automation."""
    if depth > max_depth:
        return
    indent = "  " * depth
    name = control.Name or "<Sans Nom>"
    control_type = control.ControlTypeName
    automation_id = control.AutomationId or "<Pas d'ID>"
    print(f"{indent}- [{control_type}] Name: '{name}' | ID: '{automation_id}'")
    
    # Parcourir les enfants
    for child, _ in auto.WalkControl(control, maxDepth=1):
        if child == control:
            continue
        print_element_tree(child, depth + 1, max_depth)

def main():
    print("🔍 Recherche de la fenêtre Deezer (PaneControl) avec uiautomation...")
    
    # Trouver le PaneControl ou WindowControl nommé Deezer
    deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
    
    if not deezer_ctrl.Exists(1.0):
        print("❌ Impossible de trouver la fenêtre Deezer.")
        return
        
    print(f"✔ Fenêtre trouvée ! Titre : '{deezer_ctrl.Name}' | Type : '{deezer_ctrl.ControlTypeName}'")
    print("🌳 Affichage de l'arbre d'UI Automation (DOM de l'OS) - Profondeur max 4 :")
    
    try:
        print_element_tree(deezer_ctrl, max_depth=4)
    except Exception as err:
        print(f"❌ Erreur lors du parcours : {err}")

if __name__ == "__main__":
    main()
