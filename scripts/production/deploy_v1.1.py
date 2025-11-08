#!/usr/bin/env python3

"""
Déploiement corpus v1.1 en production
Remplace les fichiers de production par le corpus raffiné et enrichi
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def backup_existing(filepath):
    """Crée une backup du fichier existant"""
    if filepath.exists():
        backup_path = filepath.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup")
        shutil.copy2(filepath, backup_path)
        print(f"   ✓ Backup : {backup_path.name}")

def main():
    print("="*60)
    print("DÉPLOIEMENT CORPUS v1.1 EN PRODUCTION")
    print("="*60)
    
    # Source : corpus raffiné et enrichi
    source_file = Path("src/data/questions/compiled_refined_enriched.json")
    if not source_file.exists():
        print(f"\n⚠️  Fichier source non trouvé : {source_file}")
        print("   Utilisation de compiled_refined.json...")
        source_file = Path("src/data/questions/compiled_refined.json")
    
    with open(source_file, "r") as f:
        refined_data = json.load(f)
    
    questions = refined_data.get("questions", refined_data)
    print(f"\n📂 Source : {source_file.name}")
    print(f"   ✓ {len(questions)} QCM à déployer")
    
    # Fichiers à mettre à jour
    targets = [
        "src/data/questions/compiled.json",
        "src/data/questions/revision.json",
        "src/data/questions/entrainement.json",
        "src/data/questions/concours.json"
    ]
    
    print(f"\n🔄 Mise à jour des fichiers de production...")
    
    for target_path in targets:
        target = Path(target_path)
        
        # Backup
        backup_existing(target)
        
        # Copie
        if target.name == "compiled.json":
            # Remplace directement compiled.json
            with open(target, "w") as f:
                json.dump(refined_data, f, ensure_ascii=False, indent=2)
        else:
            # Pour revision/entrainement/concours : met à jour les questions
            if target.exists():
                with open(target, "r") as f:
                    existing_data = json.load(f)
                
                # Met à jour avec les nouvelles questions
                if isinstance(existing_data, dict):
                    existing_data["questions"] = questions
                    existing_data["total_questions"] = len(questions)
                    existing_data["version"] = "v1.1"
                    with open(target, "w") as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                else:
                    with open(target, "w") as f:
                        json.dump(questions, f, ensure_ascii=False, indent=2)
            else:
                # Crée le fichier s'il n'existe pas
                with open(target, "w") as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ {target.name} mis à jour")
    
    print(f"\n{'='*60}")
    print(f"✅ DÉPLOIEMENT TERMINÉ")
    print(f"{'='*60}")
    print(f"📊 {len(questions)} QCM v1.1 en production")
    print(f"💾 Backups créés avec timestamp")
    print(f"{'='*60}")
    
    print(f"\n🎯 PROCHAINES ÉTAPES :")
    print(f"   1. Régénérer les 6 examens blancs")
    print(f"   2. Vérifier l'application frontend")
    print(f"   3. Créer la release GitHub v1.1")

if __name__ == "__main__":
    main()

