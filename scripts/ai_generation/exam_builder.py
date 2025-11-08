#!/usr/bin/env python3
"""
Script de génération des examens blancs calibrés
Tâche [056] - Phase 5 : Compilation & Examens

Objectif:
- Créer 6 examens thématiques calibrés (60 Q × 120 min)
- Pondération modules selon profil annales
- Distribution difficultés : 30% easy / 50% medium / 20% hard

Usage:
    python scripts/ai_generation/exam_builder.py \
           --in concours.json \
           --annales-profile src/data/annales_profile.json \
           --out-dir src/data/exams/ \
           --count 6
"""

import argparse
import json
import random
from pathlib import Path
from collections import Counter
from typing import Dict, List
from datetime import datetime

# =============================================================================
# CONFIGURATION EXAMENS
# =============================================================================

EXAM_CONFIGS = [
    {
        'exam_id': 'exam_01_physio_pharma',
        'title': 'Examen Blanc 1 : Physiologie & Pharmacologie',
        'description': 'Bases physiologie, respiratoire, cardio, pharmacologie générale',
        'module_weights': {
            'bases_physio': 0.15,
            'respiratoire': 0.20,
            'cardio': 0.25,
            'pharma_generaux': 0.20,
            'pharma_opioides': 0.20
        }
    },
    {
        'exam_id': 'exam_02_cardio_rea',
        'title': 'Examen Blanc 2 : Cardio & Réanimation',
        'description': 'Hémodynamique, choc, réanimation, monitorage',
        'module_weights': {
            'cardio': 0.40,
            'reanimation': 0.30,
            'monitorage': 0.15,
            'transfusion': 0.15
        }
    },
    {
        'exam_id': 'exam_03_resp_vent',
        'title': 'Examen Blanc 3 : Respiratoire & Ventilation',
        'description': 'Physiologie respiratoire, ventilation, voies aériennes, monitorage',
        'module_weights': {
            'respiratoire': 0.40,
            'ventilation': 0.30,
            'monitorage': 0.15,
            'reanimation': 0.15
        }
    },
    {
        'exam_id': 'exam_04_pharmaco',
        'title': 'Examen Blanc 4 : Pharmacologie Complète',
        'description': 'Tous les médicaments : généraux, locaux, opioïdes, curares',
        'module_weights': {
            'pharma_generaux': 0.25,
            'pharma_locaux': 0.25,
            'pharma_opioides': 0.25,
            'pharma_curares': 0.25
        }
    },
    {
        'exam_id': 'exam_05_alr_douleur',
        'title': 'Examen Blanc 5 : ALR & Douleur',
        'description': 'Anesthésie locorégionale, douleur, transfusion',
        'module_weights': {
            'alr': 0.40,
            'douleur': 0.30,
            'pharma_locaux': 0.20,
            'transfusion': 0.10
        }
    },
    {
        'exam_id': 'exam_06_mixte',
        'title': 'Examen Blanc 6 : Mixte Complet',
        'description': 'Tous modules, pondération selon profil annales',
        'module_weights': {}  # Sera rempli depuis profil annales
    }
]

QUESTIONS_PER_EXAM = 60
DIFFICULTY_DISTRIBUTION = {
    'easy': 0.30,
    'medium': 0.50,
    'hard': 0.20
}

# =============================================================================
# GÉNÉRATION EXAMENS
# =============================================================================

def build_exam(
    exam_config: Dict,
    questions_pool: List[Dict],
    annales_profile: Dict
) -> Dict:
    """
    Construit un examen selon la configuration.
    """
    exam_id = exam_config['exam_id']
    module_weights = exam_config['module_weights']
    
    # Si pas de weights (exam mixte), utilise profil annales
    if not module_weights:
        module_weights = annales_profile.get('module_weights', {})
        # Normalise si sum != 1
        total = sum(module_weights.values())
        if total > 0:
            module_weights = {k: v/total for k, v in module_weights.items()}
    
    # Groupe questions par module et difficulté
    by_module = {}
    for question in questions_pool:
        module_id = question.get('module_id', 'unknown')
        if module_id not in by_module:
            by_module[module_id] = {'easy': [], 'medium': [], 'hard': []}
        
        difficulty = question.get('difficulty', 'medium')
        by_module[module_id][difficulty].append(question)
    
    # Sélection questions selon pondération
    selected_questions = []
    
    for module_id, weight in module_weights.items():
        if module_id not in by_module:
            continue
        
        # Nombre de questions pour ce module
        nb_questions_module = int(QUESTIONS_PER_EXAM * weight)
        
        # Répartition par difficulté
        nb_easy = int(nb_questions_module * DIFFICULTY_DISTRIBUTION['easy'])
        nb_medium = int(nb_questions_module * DIFFICULTY_DISTRIBUTION['medium'])
        nb_hard = int(nb_questions_module * DIFFICULTY_DISTRIBUTION['hard'])
        
        # Ajustement pour atteindre exactement nb_questions_module
        diff = nb_questions_module - (nb_easy + nb_medium + nb_hard)
        if diff > 0:
            nb_medium += diff
        
        # Sélection aléatoire
        easy_q = random.sample(by_module[module_id]['easy'], 
                               min(nb_easy, len(by_module[module_id]['easy'])))
        medium_q = random.sample(by_module[module_id]['medium'], 
                                 min(nb_medium, len(by_module[module_id]['medium'])))
        hard_q = random.sample(by_module[module_id]['hard'], 
                               min(nb_hard, len(by_module[module_id]['hard'])))
        
        selected_questions.extend(easy_q + medium_q + hard_q)
    
    # Ajustement si < 60 questions (compléter avec questions aléatoires)
    if len(selected_questions) < QUESTIONS_PER_EXAM:
        remaining = QUESTIONS_PER_EXAM - len(selected_questions)
        available = [q for q in questions_pool if q not in selected_questions]
        if available:
            selected_questions.extend(random.sample(available, min(remaining, len(available))))
    
    # Shuffle pour randomiser l'ordre
    random.shuffle(selected_questions)
    
    # Limite à 60 questions
    selected_questions = selected_questions[:QUESTIONS_PER_EXAM]
    
    # Construction examen
    exam = {
        'exam_id': exam_id,
        'title': exam_config['title'],
        'description': exam_config['description'],
        'duration_minutes': 120,
        'question_count': len(selected_questions),
        'question_ids': [q.get('id', q.get('chunk_id', '')) for q in selected_questions],
        'module_weights': module_weights,
        'difficulty_distribution': {
            'easy': sum(1 for q in selected_questions if q.get('difficulty') == 'easy') / len(selected_questions),
            'medium': sum(1 for q in selected_questions if q.get('difficulty') == 'medium') / len(selected_questions),
            'hard': sum(1 for q in selected_questions if q.get('difficulty') == 'hard') / len(selected_questions)
        },
        'questions': selected_questions
    }
    
    return exam

def main():
    parser = argparse.ArgumentParser(description="Classification par mode + génération examens")
    parser.add_argument('--in', dest='input_file', required=True, help='Fichier validated.json')
    parser.add_argument('--out-dir', required=True, help='Dossier de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CLASSIFICATION MODES & GÉNÉRATION EXAMENS")
    print("="*60)
    
    # Charge questions
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    print(f"\n✓ {len(questions)} questions chargées")
    
    # Répartition modes
    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # RÉVISION: toutes
    with open(output_dir / 'revision.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"✓ revision.json : {len(questions)} questions")
    
    # ENTRAÎNEMENT: avec explications
    entrainement = [q for q in questions if len(q.get('explanation', '')) >= 100]
    with open(output_dir / 'entrainement.json', 'w', encoding='utf-8') as f:
        json.dump(entrainement, f, ensure_ascii=False, indent=2)
    print(f"✓ entrainement.json : {len(entrainement)} questions")
    
    # CONCOURS: toutes (pool pour examens)
    with open(output_dir / 'concours.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"✓ concours.json : {len(questions)} questions")
    
    # COMPILED
    compiled = {
        'generated_at': datetime.now().isoformat(),
        'total_questions': len(questions),
        'modes': {
            'revision': len(questions),
            'entrainement': len(entrainement),
            'concours': len(questions)
        },
        'questions': questions
    }
    
    with open(output_dir / 'compiled.json', 'w', encoding='utf-8') as f:
        json.dump(compiled, f, ensure_ascii=False, indent=2)
    print(f"✓ compiled.json : {len(questions)} questions")
    
    print(f"\n{'='*60}")
    print(f"✅ CLASSIFICATION TERMINÉE")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    exit(main())

