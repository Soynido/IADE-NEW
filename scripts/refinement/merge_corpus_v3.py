#!/usr/bin/env python3
"""
FUSION v3 - Préservation TOTALE
Utilise matching intelligent sans écraser les doublons
"""

import json
from pathlib import Path
from collections import Counter

def load_json(filepath):
    """Charge et extrait les questions"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "questions" in data:
        return data["questions"], data
    elif isinstance(data, list):
        return data, None
    return [], None

def main():
    print("="*60)
    print("FUSION v3 - PRÉSERVATION TOTALE")
    print("="*60)
    
    # Charge original
    original, metadata = load_json("src/data/questions/compiled.json")
    print(f"\n✓ {len(original)} questions v1.0")
    
    # Charge raffinés
    refined, _ = load_json("src/data/questions/to_refine_rescored.json")
    print(f"✓ {len(refined)} questions raffinées")
    
    # Crée set des chunk_ids raffinés pour matching
    refined_by_chunk = {}
    for r in refined:
        chunk_id = r.get('chunk_id')
        if chunk_id:
            if chunk_id not in refined_by_chunk:
                refined_by_chunk[chunk_id] = []
            refined_by_chunk[chunk_id].append(r)
    
    print(f"\n🔀 Fusion intelligente...")
    
    # Remplace question par question
    final = []
    replaced = 0
    
    for orig_q in original:
        chunk_id = orig_q.get('chunk_id')
        
        # Si ce chunk_id a des versions raffinées ET qu'il en reste
        if chunk_id in refined_by_chunk and len(refined_by_chunk[chunk_id]) > 0:
            # Pop la première version raffinée disponible
            refined_version = refined_by_chunk[chunk_id].pop(0)
            final.append(refined_version)
            replaced += 1
        else:
            # Garde l'original
            final.append(orig_q)
    
    print(f"   ✓ {replaced} questions remplacées")
    print(f"   ✓ {len(original) - replaced} questions originales conservées")
    
    # Reconstruit corpus
    if metadata:
        output = {
            **metadata,
            'total_questions': len(final),
            'refined_count': replaced,
            'version': 'v1.1',
            'generated_at': '2025-11-08T13:30:00',
            'questions': final
        }
    else:
        output = final
    
    # Sauvegarde
    with open("src/data/questions/compiled_refined.json", 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS")
    print(f"{'='*60}")
    print(f"Original    : {len(original)} QCM")
    print(f"Raffinés    : {len(refined)} QCM")
    print(f"Remplacés   : {replaced} QCM")
    print(f"Final       : {len(final)} QCM")
    
    if len(final) == len(original):
        print(f"\n✅ SUCCÈS TOTAL : {len(final)} questions préservées !")
    else:
        print(f"\n⚠️  Différence: {len(final)} vs {len(original)}")
    
    # Distribution
    modules = Counter(q.get('module_id') for q in final)
    print(f"\n📊 DISTRIBUTION PAR MODULE (top 5)")
    for module, count in modules.most_common(5):
        print(f"   {module:20} : {count:3} QCM")
    
    print(f"\n{'='*60}")
    print(f"✅ FUSION TERMINÉE - compiled_refined.json")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

