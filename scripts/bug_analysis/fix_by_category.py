#!/usr/bin/env python3
"""
Traitement des bugs PAR CATÉGORIE
Permet de récupérer et corriger tous les bugs d'un type spécifique

Usage:
    # Voir toutes les questions avec faute d'orthographe
    python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --list
    
    # Traiter les fautes d'orthographe (mode interactif)
    python scripts/bug_analysis/fix_by_category.py --category faute_orthographe
    
    # Dry-run
    python scripts/bug_analysis/fix_by_category.py --category faute_orthographe --dry-run

Catégories disponibles:
    - reponse_incorrecte
    - question_ambigue
    - plusieurs_reponses
    - explication_incorrecte
    - explication_manquante
    - reference_incorrecte
    - terme_medical_incorrect
    - faute_orthographe
    - options_repetees
    - difficulte_mal_calibree
    - hors_programme
    - autre
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

REDIS_URL = os.getenv('KV_REST_API_URL', 'https://full-crab-26762.upstash.io')
REDIS_TOKEN = os.getenv('KV_REST_API_TOKEN')

QUESTIONS_FILE = 'src/data/questions/compiled.json'
PUBLIC_QUESTIONS_FILE = 'public/data/questions/compiled.json'

# =============================================================================
# REDIS HELPERS
# =============================================================================

def get_questions_for_category(category: str) -> List[str]:
    """Récupère tous les question_ids d'une catégorie"""
    if not REDIS_TOKEN:
        print("❌ Variables Redis non configurées")
        return []
    
    try:
        response = requests.get(
            f"{REDIS_URL}/lrange/bug:{category}/0/-1",
            headers={'Authorization': f'Bearer {REDIS_TOKEN}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            question_ids = data.get('result', [])
            # Déduplique (une question peut être dans la liste plusieurs fois)
            return list(set(question_ids))
        else:
            print(f"❌ Erreur Redis: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def get_bug_details(question_id: str) -> Optional[Dict[str, Any]]:
    """Récupère les détails complets d'un bug"""
    if not REDIS_TOKEN:
        return None
    
    try:
        response = requests.get(
            f"{REDIS_URL}/get/bug_details:{question_id}",
            headers={'Authorization': f'Bearer {REDIS_TOKEN}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('result')
            if result:
                return json.loads(result) if isinstance(result, str) else result
        return None
    except Exception as e:
        print(f"⚠️  Erreur lecture bug {question_id}: {e}")
        return None

def get_category_stats() -> Dict[str, int]:
    """Récupère les stats par catégorie"""
    if not REDIS_TOKEN:
        return {}
    
    try:
        response = requests.get(
            f"{REDIS_URL}/hgetall/bug_stats:by_category",
            headers={'Authorization': f'Bearer {REDIS_TOKEN}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            # Convertit les valeurs en int
            return {k: int(v) for k, v in result.items()}
        return {}
    except Exception as e:
        print(f"⚠️  Erreur stats: {e}")
        return {}

# =============================================================================
# AFFICHAGE & HELPERS
# =============================================================================

def load_questions() -> Dict[str, Any]:
    """Charge les questions (src + public)"""
    questions = {}
    
    for filepath in [QUESTIONS_FILE, PUBLIC_QUESTIONS_FILE]:
        if not os.path.exists(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                q_list = data if isinstance(data, list) else data.get('questions', [])
                
                for q in q_list:
                    q_id = q.get('id') or q.get('chunk_id')
                    if q_id:
                        questions[q_id] = q
        except Exception as e:
            print(f"⚠️  Erreur lecture {filepath}: {e}")
    
    return questions

def display_question_with_bug(question: Dict[str, Any], bug_details: Dict[str, Any]):
    """Affiche une question avec ses bugs"""
    print(f"\n{'='*70}")
    print(f"📝 Question: {question.get('id') or question.get('chunk_id')}")
    print(f"{'='*70}")
    
    print(f"\n💬 Texte:")
    print(f"   {question.get('text', 'N/A')}")
    
    print(f"\n🎯 Options:")
    for i, opt in enumerate(question.get('options', [])):
        marker = '✅' if i == question.get('correctAnswer') else '  '
        print(f"   {marker} {chr(65+i)}. {opt}")
    
    print(f"\n📊 Métadonnées:")
    print(f"   Module: {question.get('module_id', 'N/A')}")
    print(f"   Difficulté: {question.get('difficulty', 'N/A')}")
    print(f"   Page: {question.get('page_number') or question.get('page', 'N/A')}")
    
    print(f"\n🐛 Problèmes signalés:")
    print(f"   Catégories: {', '.join(bug_details.get('categories', []))}")
    print(f"   Sévérité: {bug_details.get('severity', 'N/A')}")
    print(f"   Rapports: 1")  # TODO: compter les rapports multiples
    
    print(f"\n💭 Description:")
    print(f"   {bug_details.get('description', 'N/A')}")
    
    if bug_details.get('suggestedFix'):
        print(f"\n💡 Suggestion utilisateur:")
        print(f"   {bug_details.get('suggestedFix')}")

# =============================================================================
# COMMANDES
# =============================================================================

def cmd_list_category(category: str):
    """Liste toutes les questions d'une catégorie"""
    print(f"\n📋 Questions avec bug: {category}")
    print(f"{'='*70}")
    
    question_ids = get_questions_for_category(category)
    
    if not question_ids:
        print(f"✅ Aucune question signalée dans cette catégorie")
        return
    
    print(f"\n{len(question_ids)} question(s) trouvée(s):\n")
    
    questions = load_questions()
    
    for i, q_id in enumerate(question_ids, 1):
        bug_details = get_bug_details(q_id)
        question = questions.get(q_id)
        
        if not question:
            print(f"{i}. {q_id} - ⚠️  Question introuvable dans corpus")
            continue
        
        print(f"{i}. {q_id}")
        print(f"   Texte: {question.get('text', 'N/A')[:60]}...")
        print(f"   Module: {question.get('module_id', 'N/A')}")
        
        if bug_details:
            all_categories = bug_details.get('categories', [category])
            if len(all_categories) > 1:
                other_cats = [c for c in all_categories if c != category]
                print(f"   Autres problèmes: {', '.join(other_cats)}")

def cmd_stats():
    """Affiche les statistiques par catégorie"""
    print(f"\n📊 STATISTIQUES PAR CATÉGORIE")
    print(f"{'='*70}")
    
    stats = get_category_stats()
    
    if not stats:
        print(f"✅ Aucun bug signalé pour le moment")
        return
    
    # Tri par nombre décroissant
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Catégorie':<30} {'Count':<10} {'Priorité'}")
    print(f"{'-'*70}")
    
    for category, count in sorted_stats:
        # Détermine priorité selon catégorie
        priority = 'HIGH  ' if category in ['reponse_incorrecte', 'terme_medical_incorrect'] else \
                   'MEDIUM' if category in ['question_ambigue', 'plusieurs_reponses', 'explication_incorrecte'] else \
                   'LOW   '
        
        print(f"{category:<30} {count:<10} {priority}")
    
    print(f"\n{'Total':<30} {sum(stats.values())}")
    
    print(f"\n💡 Suggestions:")
    print(f"   1. Commencer par les bugs simples (faute_orthographe)")
    print(f"   2. Puis les bugs moyens (question_ambigue)")
    print(f"   3. Enfin les bugs critiques (reponse_incorrecte) avec validation expert")

def cmd_fix_category(category: str, dry_run: bool = False):
    """Traite tous les bugs d'une catégorie"""
    print(f"\n🔧 TRAITEMENT : {category}")
    print(f"{'='*70}")
    
    if dry_run:
        print(f"⚠️  MODE DRY-RUN : Aucune modification ne sera appliquée\n")
    
    question_ids = get_questions_for_category(category)
    
    if not question_ids:
        print(f"✅ Aucune question à traiter")
        return
    
    print(f"\n{len(question_ids)} question(s) à traiter\n")
    
    questions = load_questions()
    
    for i, q_id in enumerate(question_ids, 1):
        bug_details = get_bug_details(q_id)
        question = questions.get(q_id)
        
        if not question or not bug_details:
            print(f"[{i}/{len(question_ids)}] {q_id} - ⚠️  Données manquantes, skip")
            continue
        
        # Affiche la question et le bug
        display_question_with_bug(question, bug_details)
        
        # Demande action
        if not dry_run:
            action = input(f"\n👉 Action? (o=ouvrir pour correction / s=skip / q=quitter): ").strip().lower()
            
            if action == 'q':
                print(f"\n❌ Traitement interrompu")
                break
            elif action == 'o':
                # Ouvre dans l'éditeur (TODO)
                print(f"📝 TODO: Ouverture dans éditeur")
                print(f"   Fichier: {QUESTIONS_FILE}")
                print(f"   Question ID: {q_id}")
            else:
                print(f"⏭️  Question sautée")
    
    print(f"\n✅ Traitement de la catégorie '{category}' terminé")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Traitement des bugs par catégorie',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--category', type=str,
                       help='Catégorie à traiter (ex: faute_orthographe)')
    parser.add_argument('--list', action='store_true',
                       help='Lister les questions de la catégorie')
    parser.add_argument('--stats', action='store_true',
                       help='Afficher les stats par catégorie')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulation sans modification')
    
    args = parser.parse_args()
    
    print("🐛 TRAITEMENT BUGS PAR CATÉGORIE")
    print("="*70)
    
    # Stats globales
    if args.stats or (not args.category and not args.list):
        cmd_stats()
        return
    
    # Vérification catégorie
    if not args.category:
        print("❌ Erreur: --category requis")
        print("\nUtilisez: --stats pour voir les catégories disponibles")
        sys.exit(1)
    
    # Liste questions
    if args.list:
        cmd_list_category(args.category)
        return
    
    # Traitement
    cmd_fix_category(args.category, dry_run=args.dry_run)

if __name__ == '__main__':
    main()

