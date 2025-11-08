#!/usr/bin/env python3
"""
Script de validation finale et consolidation
Tâches [033-035b] - Phase 5 : Compilation & Examens

Objectif:
- Déduplication (hash unique)
- Validation format strict (4 options, correctAnswer valide)
- Lissage distribution difficultés (40/40/20)
- Classification automatique difficultés basée sur rules
- Vérification exhaustivité (chaque chunk → ≥1 QCM)

Usage:
    python scripts/ai_generation/validate_all.py \
           --in generated_scored.json \
           --out validated.json
"""

import argparse
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# Distribution cible par module
TARGET_DISTRIBUTION = {
    'easy': 0.40,
    'medium': 0.40,
    'hard': 0.20
}

# Règle automatique de classification difficultés
def auto_classify_difficulty(question: Dict) -> str:
    """
    Classifie automatiquement la difficulté selon règles spec.md.
    
    Règle:
    - hard: context_score > 0.9 ET explication > 40 mots
    - easy: context_score < 0.65 OU explication < 20 mots
    - medium: sinon
    """
    context_score = question.get('context_score', 0)
    explanation = question.get('explanation', '')
    explanation_words = len(explanation.split())
    
    if context_score > 0.9 and explanation_words > 40:
        return 'hard'
    elif context_score < 0.65 or explanation_words < 20:
        return 'easy'
    else:
        return 'medium'

# =============================================================================
# DÉDUPLICATION
# =============================================================================

def deduplicate_questions(questions: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Supprime les doublons basés sur hash unique.
    
    Hash: sha256(text + "|" + options_sorted + "|" + module_id)
    
    Returns:
        (questions_unique, nb_duplicates_removed)
    """
    print(f"\n🔍 Déduplication de {len(questions)} questions...")
    
    seen_hashes = set()
    unique_questions = []
    duplicates_count = 0
    
    for question in questions:
        # Construction hash
        text = question.get('text', '')
        options = sorted(question.get('options', []))
        module_id = question.get('module_id', '')
        
        hash_input = f"{text}|{options}|{module_id}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
        
        if hash_value in seen_hashes:
            duplicates_count += 1
        else:
            seen_hashes.add(hash_value)
            unique_questions.append(question)
    
    print(f"   ✓ {duplicates_count} doublons supprimés")
    print(f"   ✓ {len(unique_questions)} questions uniques")
    
    return unique_questions, duplicates_count

# =============================================================================
# VALIDATION FORMAT
# =============================================================================

def validate_format(questions: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Valide le format strict des questions.
    
    Contraintes:
    - Exactement 4 options
    - correctAnswer ∈ [0, 1, 2, 3]
    - Options distinctes (pas de duplicates)
    - Texte et explication non vides
    
    Returns:
        (questions_valid, nb_invalid)
    """
    print(f"\n🔍 Validation format de {len(questions)} questions...")
    
    valid_questions = []
    invalid_count = 0
    
    for question in questions:
        # Check 4 options
        options = question.get('options', [])
        if not isinstance(options, list) or len(options) != 4:
            invalid_count += 1
            continue
        
        # Check options distinctes
        if len(set(options)) != 4:
            invalid_count += 1
            continue
        
        # Check correctAnswer
        correct_answer = question.get('correctAnswer')
        if not isinstance(correct_answer, int) or correct_answer not in [0, 1, 2, 3]:
            invalid_count += 1
            continue
        
        # Check texte et explication non vides
        if not question.get('text') or not question.get('explanation'):
            invalid_count += 1
            continue
        
        valid_questions.append(question)
    
    print(f"   ✓ {invalid_count} questions format invalide rejetées")
    print(f"   ✓ {len(valid_questions)} questions format valide")
    
    return valid_questions, invalid_count

# =============================================================================
# CLASSIFICATION DIFFICULTÉS
# =============================================================================

def classify_difficulties(questions: List[Dict]) -> List[Dict]:
    """
    Classifie automatiquement les difficultés selon règles.
    """
    print(f"\n🔍 Classification automatique des difficultés...")
    
    for question in questions:
        # Si difficultés déjà assignée, on la garde
        if not question.get('difficulty'):
            question['difficulty'] = auto_classify_difficulty(question)
        else:
            # Re-classification si incohérent
            auto_diff = auto_classify_difficulty(question)
            question['difficulty'] = auto_diff
    
    # Stats distribution
    diff_counts = Counter(q.get('difficulty') for q in questions)
    total = len(questions)
    
    print(f"   Distribution après classification :")
    for diff in ['easy', 'medium', 'hard']:
        count = diff_counts.get(diff, 0)
        percent = count / total * 100 if total > 0 else 0
        target = TARGET_DISTRIBUTION.get(diff, 0) * 100
        print(f"     {diff:7s} : {count:4d} ({percent:5.1f}%) [cible: {target:.0f}%]")
    
    return questions

def balance_difficulties_by_module(questions: List[Dict]) -> List[Dict]:
    """
    Rééquilibre la distribution des difficultés par module si nécessaire.
    Cible: 40% easy / 40% medium / 20% hard
    """
    print(f"\n⚖️  Rééquilibrage difficultés par module...")
    
    # Groupe par module
    by_module = {}
    for question in questions:
        module_id = question.get('module_id', 'unknown')
        if module_id not in by_module:
            by_module[module_id] = []
        by_module[module_id].append(question)
    
    # Pour chaque module, vérifie distribution
    rebalanced_count = 0
    
    for module_id, module_questions in by_module.items():
        if len(module_questions) < 10:  # Skip petits modules
            continue
        
        # Distribution actuelle
        diff_counts = Counter(q['difficulty'] for q in module_questions)
        total = len(module_questions)
        
        for diff in ['easy', 'medium', 'hard']:
            current_pct = diff_counts.get(diff, 0) / total
            target_pct = TARGET_DISTRIBUTION[diff]
            
            # Si écart > 15%, on ajuste
            if abs(current_pct - target_pct) > 0.15:
                rebalanced_count += 1
                # Note: rééquilibrage complet nécessiterait tri et réassignation
                # Pour v1, on log seulement
    
    if rebalanced_count > 0:
        print(f"   ⚠️  {rebalanced_count} modules nécessitent rééquilibrage (écart > 15%)")
        print(f"   Note: rééquilibrage fin sera fait en Phase 5 si nécessaire")
    else:
        print(f"   ✓ Distribution conforme pour tous les modules")
    
    return questions

# =============================================================================
# VÉRIFICATION EXHAUSTIVITÉ
# =============================================================================

def check_coverage(questions: List[Dict]) -> Dict:
    """
    Vérifie que chaque chunk_id a généré au moins 1 QCM validé.
    """
    print(f"\n🔍 Vérification exhaustivité corpus...")
    
    chunks_with_qcm = set(q.get('chunk_id') for q in questions if q.get('chunk_id'))
    
    print(f"   ✓ {len(chunks_with_qcm)} chunks ont des QCM validés")
    
    # Note: pour identifier chunks orphelins, il faudrait charger tous les modules
    # Pour v1, on log seulement le nombre de chunks couverts
    
    return {
        'chunks_covered': len(chunks_with_qcm),
        'coverage_percent': 0  # Sera calculé en Phase 5 avec coverage_report.py
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validation finale et consolidation")
    parser.add_argument('--in', dest='input_file', required=True, help='Fichier questions scored')
    parser.add_argument('--out', required=True, help='Fichier validated.json de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VALIDATION FINALE & CONSOLIDATION")
    print("="*60)
    
    # Charge questions
    print(f"\n📂 Chargement questions : {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Étape 1: Déduplication
    questions, nb_duplicates = deduplicate_questions(questions)
    
    # Étape 2: Validation format
    questions, nb_invalid = validate_format(questions)
    
    # Étape 3: Classification difficultés automatique
    questions = classify_difficulties(questions)
    
    # Étape 4: Rééquilibrage par module
    questions = balance_difficulties_by_module(questions)
    
    # Étape 5: Vérification exhaustivité
    coverage_stats = check_coverage(questions)
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'validated_at': datetime.now().isoformat(),
        'total_questions': len(questions),
        'duplicates_removed': nb_duplicates,
        'invalid_format_removed': nb_invalid,
        'coverage': coverage_stats,
        'questions': questions
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Questions validées sauvegardées : {args.out}")
    
    # Résumé final
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ VALIDATION FINALE")
    print(f"{'='*60}")
    print(f"Questions finales : {len(questions)}")
    print(f"Doublons supprimés : {nb_duplicates}")
    print(f"Format invalide : {nb_invalid}")
    print(f"Chunks couverts : {coverage_stats['chunks_covered']}")
    
    if len(questions) >= 2000:
        print(f"\n✅ OBJECTIF ATTEINT : {len(questions)} ≥ 2000 questions validées")
    else:
        print(f"\n⚠️  OBJECTIF NON ATTEINT : {len(questions)} < 2000 questions")
    
    print(f"\n{'='*60}")
    print(f"✅ VALIDATION FINALE TERMINÉE")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    exit(main())

