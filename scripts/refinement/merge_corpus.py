#!/usr/bin/env python3

"""
FUSION INTELLIGENTE v2 — Corpus complet + raffinés = v1.1 stable
Préserve toutes les questions, même sans ID explicite.
"""

import json
from pathlib import Path
from collections import Counter

def normalize_id(q, i):
    """Génère un identifiant unique et stable pour la question"""
    return (
        q.get("chunk_id")
        or q.get("id")
        or q.get("question_id")
        or f"auto_{i:04d}"
    )

def load_questions(filepath):
    """Charge questions depuis JSON (gère format objet ou array)"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "questions" in data:
        questions = data["questions"]
        if isinstance(questions, str):  # si string JSON sérialisé
            questions = json.loads(questions)
        return questions, data
    elif isinstance(data, list):
        return data, None
    else:
        print(f"⚠️ Format inconnu pour {filepath}")
        return [], None

def main():
    print("="*60)
    print("FUSION INTELLIGENTE CORPUS v1.0 → v1.1 (robuste)")
    print("="*60)
    
    # Charge corpus dédupliqué (sans doublons chunk_id)
    print("\n📂 Chargement corpus v1.0 (dédupliqué)...")
    original_questions, original_metadata = load_questions("src/data/questions/compiled_dedup.json")
    print(f"   ✓ {len(original_questions)} questions originales")
    
    # Charge raffinés
    print("\n📂 Chargement QCM raffinés...")
    refined_questions, _ = load_questions("src/data/questions/to_refine_rescored.json")
    print(f"   ✓ {len(refined_questions)} questions raffinées")
    
    # Indexe corpus original
    print("\n🔀 Indexation et fusion...")
    original_dict = {normalize_id(q, i): q for i, q in enumerate(original_questions)}
    print(f"   ✓ {len(original_dict)} questions originales indexées")
    
    # Index raffinés
    refined_dict = {normalize_id(q, i): q for i, q in enumerate(refined_questions)}
    print(f"   ✓ {len(refined_dict)} questions raffinées indexées")
    
    # Fusion
    replaced, added, not_found = 0, 0, []
    for rid, refined_q in refined_dict.items():
        if rid in original_dict:
            original_dict[rid] = refined_q
            replaced += 1
        else:
            # Ajout si nouveau ID (ex : auto_XXXX)
            original_dict[rid] = refined_q
            added += 1
            not_found.append(rid)
    
    print(f"   ✓ {replaced} questions remplacées")
    if added > 0:
        print(f"   ✓ {added} nouvelles questions ajoutées")
    
    final_questions = list(original_dict.values())
    
    # Reconstruit le corpus final
    if original_metadata:
        final_corpus = {
            **original_metadata,
            "total_questions": len(final_questions),
            "refined_count": replaced,
            "added_count": added,
            "generated_at": "2025-11-08T13:25:00",
            "version": "v1.1",
            "questions": final_questions,
        }
    else:
        final_corpus = final_questions
    
    # Sauvegarde
    output_path = Path("src/data/questions/compiled_refined.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS FUSION")
    print(f"{'='*60}")
    print(f"Questions originales : {len(original_questions)}")
    print(f"Questions raffinées  : {len(refined_questions)}")
    print(f"Questions remplacées : {replaced}")
    print(f"Questions ajoutées   : {added}")
    print(f"Questions finales    : {len(final_questions)}")
    
    if len(final_questions) >= len(original_questions):
        print(f"\n✅ FUSION RÉUSSIE : aucune perte")
        print(f"   {replaced} améliorées ({replaced/len(final_questions)*100:.1f}%)")
    else:
        print(f"\n⚠️  ATTENTION : {len(original_questions)} → {len(final_questions)} questions (perte possible)")
    
    # Stat modules
    try:
        modules = Counter(q.get("module_id", "unknown") for q in final_questions)
        refined_modules = Counter(q.get("module_id", "unknown") for q in refined_questions)
        
        print(f"\n📊 TOP 5 MODULES AMÉLIORÉS")
        for module, count in refined_modules.most_common(5):
            total = modules[module]
            percent = count / total * 100 if total > 0 else 0
            print(f"   {module:20} : {count:3}/{total:3} raffinés ({percent:.1f}%)")
    except Exception as e:
        print(f"⚠️ Impossible d'analyser la distribution par module : {e}")
    
    print(f"\n💾 Corpus fusionné : {output_path}")
    print(f"{'='*60}")
    print("✅ FUSION TERMINÉE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
