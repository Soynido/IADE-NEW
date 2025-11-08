#!/usr/bin/env python3
"""
Phase 10 - Filtrage QCM à réviser
Isole les questions avec scores sous-optimaux
"""

import json
from pathlib import Path
from collections import Counter

# Seuils de qualité (questions EN DESSOUS nécessitent révision)
BIOMEDICAL_SCORE_MIN = 0.08
CONTEXT_SCORE_MIN = 0.75
KEYWORDS_OVERLAP_MIN = 0.5
STYLISTIC_DISTANCE_MAX = 0.35

def main():
    print("="*60)
    print("FILTRAGE QCM À RÉVISER")
    print("="*60)
    
    # Charge compiled.json
    compiled_path = Path("src/data/questions/compiled.json")
    with open(compiled_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data if isinstance(data, list) else data.get('questions', [])
    
    print(f"\n📊 {len(questions)} questions totales chargées")
    
    # Filtrage
    to_refine = []
    rejection_reasons = Counter()
    
    for q in questions:
        reasons = []
        
        # Vérifie chaque critère
        bio_score = q.get("biomedical_score", 1.0)
        context_score = q.get("context_score", 1.0)
        keywords_overlap = q.get("keywords_overlap", 1.0)
        stylistic_distance = q.get("stylistic_distance", 0.0)
        
        if bio_score < BIOMEDICAL_SCORE_MIN:
            reasons.append("biomedical_score_low")
        
        if context_score < CONTEXT_SCORE_MIN:
            reasons.append("context_score_low")
        
        if keywords_overlap < KEYWORDS_OVERLAP_MIN:
            reasons.append("keywords_overlap_low")
        
        if stylistic_distance > STYLISTIC_DISTANCE_MAX:
            reasons.append("stylistic_distance_high")
        
        # Si au moins 1 raison, à réviser
        if reasons:
            q['refinement_reasons'] = reasons
            to_refine.append(q)
            
            for reason in reasons:
                rejection_reasons[reason] += 1
    
    # Stats
    refine_percent = len(to_refine) / len(questions) * 100 if questions else 0
    
    print(f"\n📊 RÉSULTATS FILTRAGE")
    print(f"  Questions à réviser  : {len(to_refine)} ({refine_percent:.1f}%)")
    print(f"  Questions OK         : {len(questions) - len(to_refine)} ({100-refine_percent:.1f}%)")
    
    print(f"\n📋 RAISONS DE RÉVISION")
    for reason, count in rejection_reasons.most_common():
        print(f"  {reason:30} : {count:4} questions")
    
    # Distribution par module
    module_counts = Counter(q['module_id'] for q in to_refine)
    print(f"\n📊 PAR MODULE (top 5)")
    for module, count in module_counts.most_common(5):
        total_module = len([q for q in questions if q['module_id'] == module])
        percent = count / total_module * 100 if total_module > 0 else 0
        print(f"  {module:20} : {count:3}/{total_module:3} à réviser ({percent:.1f}%)")
    
    # Sauvegarde
    output_path = Path("src/data/questions/to_refine.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(to_refine, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Questions à réviser sauvegardées : {output_path}")
    
    # Recommandations
    print(f"\n💡 PROCHAINES ÉTAPES")
    if refine_percent < 10:
        print(f"  ✅ Excellent ! Seulement {refine_percent:.1f}% nécessitent révision")
        print(f"  → Refinement optionnel, qualité déjà élevée")
    elif refine_percent < 25:
        print(f"  ⚠️  {refine_percent:.1f}% à réviser (normal)")
        print(f"  → Lancer refinement pour optimiser")
    else:
        print(f"  ❌ {refine_percent:.1f}% à réviser (élevé)")
        print(f"  → Refinement recommandé + ajustement seuils génération")
    
    print(f"\n🚀 COMMANDE SUIVANTE")
    print(f"  python scripts/ai_generation/refine_questions.py")
    
    print(f"\n{'='*60}")
    print(f"✅ FILTRAGE TERMINÉ")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

