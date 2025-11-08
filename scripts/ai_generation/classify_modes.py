#!/usr/bin/env python3
"""
Script de classification par mode pédagogique
Tâche [036] - Phase 5 : Compilation & Examens

Objectif:
- Répartir questions entre révision / entraînement / concours
- Critères selon difficulté et granularité

Usage:
    python scripts/ai_generation/classify_modes.py \
           --in validated.json \
           --out-dir src/data/questions/
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def classify_question_mode(question: Dict) -> str:
    """
    Classifie une question dans un mode pédagogique.
    
    Critères:
    - Révision: toutes difficultés, explications détaillées
    - Entraînement: distribution équilibrée
    - Concours: selon pondération annales
    """
    # Pour v1, répartition simple:
    # - Révision: toutes les questions (liste complète)
    # - Entraînement: subset équilibré par difficulté
    # - Concours: subset pour examens blancs
    
    # Toutes les questions vont dans révision
    # Entraînement et concours seront des subsets
    return 'all'  # On va distribuer après

def distribute_questions(questions: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Distribue les questions entre les 3 modes.
    """
    print(f"\n📊 Distribution des {len(questions)} questions par mode...")
    
    # Groupe par module et difficulté
    by_module_diff = {}
    
    for question in questions:
        module_id = question.get('module_id', 'unknown')
        difficulty = question.get('difficulty', 'medium')
        
        key = f"{module_id}_{difficulty}"
        if key not in by_module_diff:
            by_module_diff[key] = []
        by_module_diff[key].append(question)
    
    # Répartition:
    # - RÉVISION: toutes les questions (800+)
    # - ENTRAÎNEMENT: questions avec explications moyennes/détaillées (800+)
    # - CONCOURS: questions pour examens blancs (800+)
    
    revision_questions = []
    entrainement_questions = []
    concours_questions = []
    
    for question in questions:
        explanation_length = len(question.get('explanation', ''))
        
        # Toutes → Révision
        revision_questions.append({**question, 'mode': 'revision'})
        
        # Explications détaillées → Entraînement
        if explanation_length >= 100:
            entrainement_questions.append({**question, 'mode': 'entrainement'})
        
        # Toutes (seront sélectionnées pour examens) → Concours
        concours_questions.append({**question, 'mode': 'concours'})
    
    print(f"   ✓ Révision: {len(revision_questions)} questions")
    print(f"   ✓ Entraînement: {len(entrainement_questions)} questions")
    print(f"   ✓ Concours: {len(concours_questions)} questions")
    
    return {
        'revision': revision_questions,
        'entrainement': entrainement_questions,
        'concours': concours_questions
    }

def main():
    parser = argparse.ArgumentParser(description="Classification par mode pédagogique")
    parser.add_argument('--in', dest='input_file', required=True, help='Fichier validated.json')
    parser.add_argument('--out-dir', required=True, help='Dossier de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CLASSIFICATION PAR MODE PÉDAGOGIQUE")
    print("="*60)
    
    # Charge questions
    print(f"\n📂 Chargement questions : {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Distribution
    modes = distribute_questions(questions)
    
    # Sauvegarde chaque mode
    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for mode_name, mode_questions in modes.items():
        output_file = output_dir / f"{mode_name}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mode_questions, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ {output_file.name} : {len(mode_questions)} questions")
    
    # Génération compiled.json (union)
    compiled_file = output_dir / "compiled.json"
    compiled_data = {
        'generated_at': datetime.now().isoformat(),
        'total_questions': len(questions),
        'modes': {
            'revision': len(modes['revision']),
            'entrainement': len(modes['entrainement']),
            'concours': len(modes['concours'])
        },
        'questions': questions
    }
    
    with open(compiled_file, 'w', encoding='utf-8') as f:
        json.dump(compiled_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ compiled.json : {len(questions)} questions")
    
    print(f"\n{'='*60}")
    print(f"✅ CLASSIFICATION TERMINÉE")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    exit(main())

