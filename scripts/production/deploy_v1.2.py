#!/usr/bin/env python3

"""
Déploiement corpus v1.2 en production
Corpus aligné sémantiquement avec précision optimale
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
    print("DÉPLOIEMENT CORPUS v1.2 EN PRODUCTION")
    print("="*60)
    
    # Source : corpus aligné sémantiquement
    source_file = Path("src/data/questions/compiled_refined_aligned.json")
    
    if not source_file.exists():
        print(f"\n⚠️  Fichier source non trouvé : {source_file}")
        return
    
    with open(source_file, "r", encoding="utf-8") as f:
        aligned_data = json.load(f)
    
    questions = aligned_data.get("questions", aligned_data)
    print(f"\n📂 Source : {source_file.name}")
    print(f"   ✓ {len(questions)} QCM à déployer")
    
    # Statistiques
    from collections import Counter
    pdf_dist = Counter(q.get("source_pdf") for q in questions)
    avg_score = sum(q.get("alignment_score", 0) for q in questions) / len(questions)
    high_conf = sum(1 for q in questions if q.get("alignment_score", 0) >= 0.5)
    
    print(f"\n📊 Statistiques corpus v1.2:")
    print(f"   • Score alignement moyen : {avg_score:.3f}")
    print(f"   • Haute confiance (≥0.5) : {high_conf}/{len(questions)} ({high_conf/len(questions)*100:.1f}%)")
    print(f"   • Distribution PDF :")
    for pdf, count in pdf_dist.most_common():
        print(f"     - {pdf}: {count} QCM ({count/len(questions)*100:.1f}%)")
    
    # Fichiers à mettre à jour
    targets = [
        "src/data/questions/compiled.json",
        "src/data/questions/revision.json",
        "src/data/questions/entrainement.json",
        "src/data/questions/concours.json",
        "public/data/questions/compiled.json",
        "public/data/questions/revision.json",
        "public/data/questions/entrainement.json",
        "public/data/questions/concours.json"
    ]
    
    print(f"\n🔄 Mise à jour des fichiers de production...")
    
    for target_path in targets:
        target = Path(target_path)
        
        if not target.exists():
            print(f"   ⊘ {target.name} (n'existe pas, skip)")
            continue
        
        # Backup
        backup_existing(target)
        
        # Copie
        if target.name == "compiled.json":
            # Met à jour version
            aligned_data["version"] = "v1.2_semantic_aligned"
            aligned_data["total_questions"] = len(questions)
            
            with open(target, "w", encoding="utf-8") as f:
                json.dump(aligned_data, f, ensure_ascii=False, indent=2)
        else:
            # Pour revision/entrainement/concours
            with open(target, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            # Met à jour avec les nouvelles questions alignées
            if isinstance(existing_data, dict):
                existing_data["questions"] = questions
                existing_data["total_questions"] = len(questions)
                existing_data["version"] = "v1.2_semantic_aligned"
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
            else:
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ {target} mis à jour")
    
    print(f"\n{'='*60}")
    print(f"✅ DÉPLOIEMENT v1.2 TERMINÉ")
    print(f"{'='*60}")
    print(f"📊 {len(questions)} QCM v1.2 en production")
    print(f"🎯 Score alignement : {avg_score:.3f}")
    print(f"💾 Backups créés avec timestamp")
    print(f"{'='*60}")
    
    print(f"\n🎯 PROCHAINES ÉTAPES :")
    print(f"   1. npm run build")
    print(f"   2. vercel --prod")
    print(f"   3. gh release create v1.2")

if __name__ == "__main__":
    main()

