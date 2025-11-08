#!/usr/bin/env python3

"""
Enrichissement des métadonnées - Phase 10+
Ajoute source_pdf, page_number, difficulty pour chaque QCM
"""

import json
from pathlib import Path

def load_modules_metadata():
    """Charge les métadonnées des modules (mapping chunk -> PDF + page)"""
    modules_dir = Path("src/data/modules")
    mapping = {}
    
    for module_file in modules_dir.glob("*.json"):
        with open(module_file, "r") as f:
            module_data = json.load(f)
        
        # Parcours les sections/chunks
        for section in module_data.get("sections", []):
            for chunk in section.get("chunks", []):
                chunk_id = chunk.get("chunk_id")
                if chunk_id:
                    mapping[chunk_id] = {
                        "source_pdf": chunk.get("source_pdf", "Prepaconcoursiade-Complet.pdf"),
                        "page_number": chunk.get("page_start", 0),
                        "module_id": module_data.get("module_id")
                    }
    
    return mapping

def infer_difficulty(question):
    """Infère la difficulté d'un QCM selon des heuristiques"""
    score = question.get("biomedical_score", 0)
    explanation_len = len(question.get("explanation", ""))
    
    # Règles de difficulté
    if score > 0.95 and explanation_len > 150:
        return "hard"
    elif score > 0.90 and explanation_len > 100:
        return "medium"
    else:
        return "easy"

def main():
    print("="*60)
    print("ENRICHISSEMENT MÉTADONNÉES — Phase 10+")
    print("="*60)
    
    # Charge mapping chunk -> PDF/page
    print("\n📂 Chargement mapping modules...")
    chunk_mapping = load_modules_metadata()
    print(f"   ✓ {len(chunk_mapping)} chunks mappés")
    
    # Charge corpus v1.1
    print("\n📂 Chargement corpus v1.1...")
    with open("src/data/questions/compiled_refined.json", "r") as f:
        data = json.load(f)
    
    questions = data.get("questions", data)
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Enrichissement
    print("\n🔧 Enrichissement des métadonnées...")
    enriched = 0
    
    for q in questions:
        chunk_id = q.get("chunk_id")
        
        # Ajoute source_pdf et page_number si disponible
        if chunk_id and chunk_id in chunk_mapping:
            metadata = chunk_mapping[chunk_id]
            q["source_pdf"] = metadata["source_pdf"]
            q["page_number"] = metadata["page_number"]
            enriched += 1
        else:
            # Fallback
            q["source_pdf"] = q.get("source_pdf", "Prepaconcoursiade-Complet.pdf")
            q["page_number"] = q.get("page_number", 0)
        
        # Infère la difficulté si absente
        if "difficulty" not in q or not q["difficulty"]:
            q["difficulty"] = infer_difficulty(q)
    
    print(f"   ✓ {enriched} questions enrichies avec PDF/page")
    print(f"   ✓ {len(questions)} questions avec difficulté assignée")
    
    # Distribution des difficultés
    from collections import Counter
    diff_dist = Counter(q.get("difficulty") for q in questions)
    print(f"\n📊 Distribution des difficultés:")
    for diff, count in diff_dist.most_common():
        pct = (count / len(questions)) * 100
        print(f"   {diff:10} : {count:3} QCM ({pct:.1f}%)")
    
    # Sauvegarde
    data["questions"] = questions
    data["metadata_version"] = "v1.1_enriched"
    data["total_questions"] = len(questions)
    
    with open("src/data/questions/compiled_refined_enriched.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ ENRICHISSEMENT TERMINÉ")
    print(f"{'='*60}")
    print(f"💾 Sauvegardé : compiled_refined_enriched.json")
    print(f"📈 {len(questions)} QCM avec métadonnées complètes")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

