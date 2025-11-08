#!/usr/bin/env python3

"""
Ajoute des 'id' uniques aux questions du corpus v1.1 pour compatibilité
"""

import json
from pathlib import Path

def main():
    print("="*60)
    print("AJOUT ID UNIQUES — Compatibilité examens")
    print("="*60)
    
    # Charge corpus
    corpus_file = Path("src/data/questions/compiled.json")
    with open(corpus_file, "r") as f:
        data = json.load(f)
    
    questions = data["questions"]
    print(f"\n✓ {len(questions)} QCM chargés")
    
    # Ajoute des ID basés sur chunk_id + index
    added = 0
    for i, q in enumerate(questions):
        if "id" not in q or not q["id"]:
            # Génère ID basé sur chunk_id ou index
            chunk_id = q.get("chunk_id", f"unknown_{i}")
            q["id"] = f"{chunk_id}_q{i+1}"
            added += 1
    
    print(f"✓ {added} IDs ajoutés")
    
    # Sauvegarde
    with open(corpus_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Met à jour aussi les autres fichiers
    for file_name in ["revision.json", "entrainement.json", "concours.json"]:
        file_path = Path(f"src/data/questions/{file_name}")
        if file_path.exists():
            with open(file_path, "r") as f:
                file_data = json.load(f)
            
            # Gère les deux formats possibles
            if isinstance(file_data, dict):
                file_questions = file_data.get("questions", [])
            else:
                file_questions = file_data
            
            for i, q in enumerate(file_questions):
                if "id" not in q or not q["id"]:
                    chunk_id = q.get("chunk_id", f"unknown_{i}")
                    q["id"] = f"{chunk_id}_q{i+1}"
            
            # Reconstruit le format
            if isinstance(file_data, dict):
                file_data["questions"] = file_questions
                output = file_data
            else:
                output = file_questions
            
            with open(file_path, "w") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"✓ {file_name} mis à jour")
    
    print(f"\n{'='*60}")
    print(f"✅ IDS AJOUTÉS — Corpus compatible")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

