#!/usr/bin/env python3
"""
Script d'analyse stylistique des annales
Tâche [024] - Phase 2 : Indexation & Alignement

Objectif:
- Parser les annales corrigées (Volumes 1 & 2)
- Extraire profil stylistique : longueur énoncés, structure syntaxique, pondération modules
- Générer annales_profile.json pour calibrer les prompts Mistral

Usage:
    python scripts/analyze_annales.py --annales "src/data/sources/annalescorrigées-*.pdf" \
                                       --out src/data/annales_profile.json
"""

import argparse
import json
import re
import glob
from pathlib import Path
from collections import Counter
from typing import List, Dict

try:
    import pdfplumber
except ImportError:
    print("❌ Dépendance manquante. Installez: pip install pdfplumber")
    exit(1)

# =============================================================================
# PATTERNS DE DÉTECTION
# =============================================================================

# Patterns pour détecter les questions
QUESTION_PATTERNS = [
    r'^[0-9]+[.)]\s+(.+\?)',  # 1. Question ?
    r'^Question\s+[0-9]+\s*[:\-–]?\s*(.+\?)',  # Question 1 : Text ?
    r'^(Quelle?.+\?)',  # Quelle/Quel...?
    r'^(Parmi.+\?)',  # Parmi...?
    r'^(Concernant.+\?)',  # Concernant...?
    r'^(Dans.+\?)',  # Dans...?
    r'^(Chez.+\?)',  # Chez...?
    r'^(Lors.+\?)',  # Lors...?
]

# Débuts de phrases typiques des QCM IADE
COMMON_STARTERS = [
    "Quelle est",
    "Quelle sont",
    "Quel est",
    "Quels sont",
    "Parmi les propositions",
    "Parmi les suivantes",
    "Concernant",
    "Dans le cas",
    "Chez un patient",
    "Lors de",
    "En cas de",
    "La dose de",
    "Le traitement",
    "L'indication",
]

# =============================================================================
# FONCTIONS D'EXTRACTION
# =============================================================================

def extract_questions_from_pdf(pdf_path: str) -> List[str]:
    """
    Extrait les questions des annales (heuristiques).
    
    Returns:
        Liste de textes de questions
    """
    questions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Split en lignes
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Check si la ligne correspond à un pattern de question
                    for pattern in QUESTION_PATTERNS:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            question_text = match.group(1) if match.lastindex else line
                            if len(question_text) > 20:  # Filtre questions trop courtes
                                questions.append(question_text)
                            break
        
        return questions
        
    except Exception as e:
        print(f"⚠️  Erreur extraction {Path(pdf_path).name}: {e}")
        return []

def analyze_question_length(questions: List[str]) -> Dict:
    """Analyse la longueur des questions."""
    if not questions:
        return {'avg_chars': 0, 'avg_words': 0, 'min': 0, 'max': 0}
    
    lengths_chars = [len(q) for q in questions]
    lengths_words = [len(q.split()) for q in questions]
    
    return {
        'avg_chars': sum(lengths_chars) / len(lengths_chars),
        'avg_words': sum(lengths_words) / len(lengths_words),
        'min_chars': min(lengths_chars),
        'max_chars': max(lengths_chars),
        'median_chars': sorted(lengths_chars)[len(lengths_chars) // 2]
    }

def analyze_structure(questions: List[str]) -> Dict:
    """Analyse la structure syntaxique des questions."""
    starters_count = Counter()
    
    for question in questions:
        question_lower = question.lower()
        
        # Check débuts de phrases communs
        for starter in COMMON_STARTERS:
            if question_lower.startswith(starter.lower()):
                starters_count[starter] += 1
                break
    
    # Top 10 starters
    top_starters = [starter for starter, _ in starters_count.most_common(10)]
    
    return {
        'common_starters': top_starters,
        'starter_distribution': dict(starters_count.most_common(15))
    }

def classify_question_type(question: str) -> str:
    """
    Classifie le type de question.
    
    Returns:
        'qcm_simple' | 'calcul' | 'qroc' | 'cas_clinique'
    """
    question_lower = question.lower()
    
    # Détection de calculs
    if any(word in question_lower for word in ['calculer', 'calculez', 'dose', 'posologie', 'débit']):
        if re.search(r'\d+\s*(mg|ml|kg|g|mmol)', question_lower):
            return 'calcul'
    
    # Détection de cas cliniques (énoncé long)
    if len(question) > 300:
        return 'cas_clinique'
    
    # Détection QROC (question ouverte)
    if any(word in question_lower for word in ['expliquez', 'décrivez', 'définissez']):
        return 'qroc'
    
    return 'qcm_simple'

def analyze_question_types(questions: List[str]) -> Dict:
    """Analyse les types de questions."""
    types_count = Counter()
    
    for question in questions:
        q_type = classify_question_type(question)
        types_count[q_type] += 1
    
    total = len(questions)
    distribution = {
        q_type: {
            'count': count,
            'percent': (count / total * 100) if total > 0 else 0
        }
        for q_type, count in types_count.items()
    }
    
    return distribution

def estimate_module_weights(questions: List[str]) -> Dict[str, float]:
    """
    Estime la pondération des modules basée sur mots-clés des questions.
    """
    # Mots-clés identifiant les modules
    module_keywords_map = {
        "cardio": ["cœur", "cardiaque", "pression", "artérielle", "hémodynamique", "choc", "débit"],
        "respiratoire": ["respiration", "ventilation", "PEEP", "oxygène", "PaO2", "saturation"],
        "pharma": ["médicament", "drug", "dose", "posologie", "morphine", "propofol", "anesthésique"],
        "neuro": ["neurologie", "conscience", "GCS", "PIC", "cérébral"],
        "transfusion": ["sang", "transfusion", "CGR", "plaquettes", "hémostase"],
        "douleur": ["douleur", "analgésie", "EVA", "échelle"],
        "reanimation": ["réanimation", "sepsis", "SDRA", "défaillance"],
    }
    
    module_scores = Counter()
    
    for question in questions:
        question_lower = question.lower()
        
        for module, keywords in module_keywords_map.items():
            score = sum(1 for kw in keywords if kw in question_lower)
            if score > 0:
                module_scores[module] += score
    
    # Normalisation en pourcentages
    total = sum(module_scores.values())
    weights = {
        module: (count / total) if total > 0 else 0
        for module, count in module_scores.items()
    }
    
    return weights

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyse stylistique des annales")
    parser.add_argument('--annales', required=True, help='Pattern glob des PDF annales')
    parser.add_argument('--out', required=True, help='Fichier annales_profile.json de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("ANALYSE STYLISTIQUE DES ANNALES")
    print("="*60)
    
    # Trouve les fichiers annales
    annales_files = glob.glob(args.annales)
    if not annales_files:
        print(f"❌ Aucun fichier trouvé pour: {args.annales}")
        return 1
    
    print(f"\n📁 {len(annales_files)} fichiers annales trouvés")
    
    # Extraction de toutes les questions
    all_questions = []
    
    for annales_path in annales_files:
        print(f"\n📄 Analyse de : {Path(annales_path).name}")
        questions = extract_questions_from_pdf(annales_path)
        print(f"   ✓ {len(questions)} questions extraites")
        all_questions.extend(questions)
    
    if not all_questions:
        print("\n❌ Aucune question extraite")
        return 1
    
    print(f"\n✓ Total : {len(all_questions)} questions")
    
    # Analyses
    print("\n🔍 Analyse de la longueur...")
    length_stats = analyze_question_length(all_questions)
    
    print("\n🔍 Analyse de la structure...")
    structure_stats = analyze_structure(all_questions)
    
    print("\n🔍 Analyse des types de questions...")
    types_stats = analyze_question_types(all_questions)
    
    print("\n🔍 Estimation pondération modules...")
    module_weights = estimate_module_weights(all_questions)
    
    # Génération du profil
    profile = {
        'total_questions_analyzed': len(all_questions),
        'avg_question_length': round(length_stats['avg_chars']),
        'avg_question_words': round(length_stats['avg_words']),
        'length_range': {
            'min': length_stats['min_chars'],
            'max': length_stats['max_chars'],
            'median': length_stats['median_chars']
        },
        'common_starters': structure_stats['common_starters'],
        'starter_distribution': structure_stats['starter_distribution'],
        'question_types': types_stats,
        'module_weights': module_weights,
        'difficulty_distribution': {
            'easy': 0.30,
            'medium': 0.50,
            'hard': 0.20
        }
    }
    
    # Affichage résumé
    print("\n" + "="*60)
    print("📊 PROFIL DES ANNALES")
    print("="*60)
    print(f"Questions analysées : {profile['total_questions_analyzed']}")
    print(f"Longueur moyenne : {profile['avg_question_length']} caractères ({profile['avg_question_words']} mots)")
    print(f"Range : {profile['length_range']['min']} - {profile['length_range']['max']} caractères")
    print(f"\nDébuts fréquents :")
    for starter in profile['common_starters'][:5]:
        count = profile['starter_distribution'].get(starter, 0)
        print(f"  - \"{starter}\" : {count} occurrences")
    
    print(f"\nTypes de questions :")
    for q_type, stats in profile['question_types'].items():
        print(f"  - {q_type}: {stats['count']} ({stats['percent']:.1f}%)")
    
    print(f"\nPondération modules estimée :")
    for module, weight in sorted(module_weights.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {module}: {weight*100:.1f}%")
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Profil sauvegardé : {args.out}")
    
    print("\n" + "="*60)
    print("✅ ANALYSE TERMINÉE")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())

