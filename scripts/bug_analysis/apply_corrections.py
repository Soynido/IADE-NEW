#!/usr/bin/env python3
"""
Application des corrections de bugs
Script INTERACTIF - Ne corrige RIEN automatiquement sans confirmation

Usage:
    # Mode interactif (recommandé)
    python scripts/bug_analysis/apply_corrections.py
    
    # Voir les corrections sans appliquer (dry-run)
    python scripts/bug_analysis/apply_corrections.py --dry-run
    
    # Appliquer UNIQUEMENT les corrections auto-safe (avec confirmation)
    python scripts/bug_analysis/apply_corrections.py --auto-only

⚠️  IMPORTANT : Ce script NE FAIT RIEN sans votre accord explicite
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import shutil

# =============================================================================
# CONFIGURATION
# =============================================================================

CORRECTIONS_FILE = 'reports/bug_corrections_proposed.json'
QUESTIONS_FILE = 'src/data/questions/compiled.json'
BACKUP_DIR = 'backups/bug_fixes'

# =============================================================================
# HELPERS
# =============================================================================

def load_corrections() -> Dict[str, Any]:
    """Charge les corrections proposées"""
    if not os.path.exists(CORRECTIONS_FILE):
        print(f"❌ Fichier introuvable: {CORRECTIONS_FILE}")
        print("💡 Lancer d'abord: python scripts/bug_analysis/analyze_bug_reports.py")
        sys.exit(1)
    
    with open(CORRECTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_questions() -> List[Dict[str, Any]]:
    """Charge les questions depuis compiled.json"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('questions', [])

def save_questions(questions: List[Dict[str, Any]], backup: bool = True):
    """Sauvegarde les questions avec backup optionnel"""
    
    # Backup avant modification
    if backup:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{BACKUP_DIR}/compiled_{timestamp}.json"
        shutil.copy2(QUESTIONS_FILE, backup_file)
        print(f"💾 Backup créé: {backup_file}")
    
    # Sauvegarde
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fichier mis à jour: {QUESTIONS_FILE}")

def find_question_by_id(questions: List[Dict[str, Any]], question_id: str) -> tuple:
    """Trouve une question par ID, retourne (index, question)"""
    for i, q in enumerate(questions):
        q_id = q.get('id') or q.get('chunk_id')
        if q_id == question_id:
            return i, q
    return None, None

# =============================================================================
# APPLICATION DES CORRECTIONS
# =============================================================================

def apply_correction(
    questions: List[Dict[str, Any]], 
    correction: Dict[str, Any],
    dry_run: bool = False
) -> bool:
    """Applique une correction (ou simule si dry_run)"""
    
    question_id = correction['question_id']
    category = correction['issue_category']
    
    idx, question = find_question_by_id(questions, question_id)
    
    if question is None:
        print(f"⚠️  Question introuvable: {question_id}")
        return False
    
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Question: {question_id}")
    print(f"🏷️  Catégorie: {category}")
    print(f"📊 Priorité: {correction['priority']}")
    print(f"🎯 Confiance: {correction['confidence']:.2f}")
    
    # Affichage détails
    print(f"\n📖 Question actuelle:")
    print(f"   {question.get('text', 'N/A')[:100]}...")
    print(f"\n   Réponse correcte: {question.get('correctAnswer')}")
    print(f"   Difficulté: {question.get('difficulty', 'N/A')}")
    
    print(f"\n💬 Descriptions utilisateurs:")
    for desc in correction['user_descriptions'][:3]:
        print(f"   • {desc[:80]}...")
    
    print(f"\n🔧 Action proposée:")
    print(f"   {correction['proposed_action']}")
    
    # Selon la catégorie, proposer modification spécifique
    if category == 'difficulte_mal_calibree':
        return apply_difficulty_fix(question, correction, dry_run)
    elif category == 'faute_orthographe':
        return apply_spelling_fix(question, correction, dry_run)
    elif category == 'reference_incorrecte':
        return apply_reference_fix(question, correction, dry_run)
    else:
        print(f"\n⚠️  Correction manuelle requise pour: {category}")
        return False

def apply_difficulty_fix(question: Dict[str, Any], correction: Dict[str, Any], dry_run: bool) -> bool:
    """Recalcule et corrige la difficulté"""
    
    # Analyse pour déterminer bonne difficulté
    # Basé sur : biomedical_score, context_score, longueur explication
    
    biomedical = question.get('biomedical_score', 0.5)
    context = question.get('context_score', 0.5)
    explanation_len = len(question.get('explanation', '').split())
    
    # Logique de classification (identique à validate_all.py)
    if context > 0.9 and explanation_len > 40:
        new_difficulty = 'hard'
    elif context < 0.65 or explanation_len < 20:
        new_difficulty = 'easy'
    else:
        new_difficulty = 'medium'
    
    old_difficulty = question.get('difficulty', 'unknown')
    
    print(f"\n🔄 Recalcul difficulté:")
    print(f"   Ancienne: {old_difficulty}")
    print(f"   Nouvelle: {new_difficulty}")
    print(f"   Scores: BioBERT={biomedical:.2f}, Context={context:.2f}, Expl={explanation_len} mots")
    
    if old_difficulty == new_difficulty:
        print(f"   ℹ️  Pas de changement nécessaire")
        return False
    
    if not dry_run:
        question['difficulty'] = new_difficulty
        return True
    
    return True

def apply_spelling_fix(question: Dict[str, Any], correction: Dict[str, Any], dry_run: bool) -> bool:
    """Correction orthographique (TODO: intégrer correcteur)"""
    print(f"\n⚠️  Correction orthographique automatique non implémentée")
    print(f"   → Révision manuelle recommandée")
    return False

def apply_reference_fix(question: Dict[str, Any], correction: Dict[str, Any], dry_run: bool) -> bool:
    """Correction référence PDF (si suggestion fournie)"""
    
    # Vérifier si utilisateurs ont suggéré nouvelle page
    suggested_pages = []
    for desc in correction['user_descriptions']:
        # Parser descriptions pour trouver "page XX"
        import re
        matches = re.findall(r'page\s+(\d+)', desc, re.IGNORECASE)
        suggested_pages.extend([int(m) for m in matches])
    
    if not suggested_pages:
        print(f"\n⚠️  Aucune suggestion de page trouvée")
        return False
    
    # Page la plus suggérée
    from collections import Counter
    most_common_page = Counter(suggested_pages).most_common(1)[0][0]
    
    old_page = question.get('page') or question.get('page_number')
    
    print(f"\n🔄 Correction référence:")
    print(f"   Ancienne page: {old_page}")
    print(f"   Nouvelle page: {most_common_page} (suggérée {suggested_pages.count(most_common_page)}x)")
    
    if not dry_run:
        question['page'] = most_common_page
        question['page_number'] = most_common_page
        return True
    
    return True

# =============================================================================
# INTERFACE INTERACTIVE
# =============================================================================

def confirm_action(message: str) -> bool:
    """Demande confirmation utilisateur"""
    response = input(f"\n{message} (o/N): ").strip().lower()
    return response in ['o', 'oui', 'y', 'yes']

def interactive_mode(corrections_data: Dict[str, Any], dry_run: bool = False):
    """Mode interactif de correction"""
    
    corrections = corrections_data['corrections']
    summary = corrections_data['summary']
    
    print(f"\n📊 RÉSUMÉ DES CORRECTIONS")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total corrections: {summary['total_corrections']}")
    print(f"Auto-corrigeables: {summary['auto_fixable']}")
    print(f"Haute priorité (≥70): {summary['high_priority']}")
    print(f"Haute confiance (≥0.7): {summary['high_confidence']}")
    
    if not corrections:
        print(f"\n✅ Aucune correction à appliquer")
        return
    
    # Filtre corrections appliquables
    auto_safe = [c for c in corrections if c['auto_fixable'] and c['confidence'] >= 0.7]
    
    print(f"\n🔧 CORRECTIONS AUTO-SAFE")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Trouvées: {len(auto_safe)}")
    
    if auto_safe:
        print(f"\nCatégories:")
        from collections import Counter
        categories = Counter(c['issue_category'] for c in auto_safe)
        for cat, count in categories.items():
            print(f"  • {cat}: {count}")
    
    if not auto_safe:
        print(f"\n⚠️  Aucune correction auto-safe disponible")
        print(f"   Toutes les corrections nécessitent révision manuelle")
        return
    
    # Confirmation globale
    if not dry_run:
        if not confirm_action(f"Appliquer les {len(auto_safe)} corrections auto-safe ?"):
            print(f"\n❌ Opération annulée")
            return
    
    # Chargement questions
    print(f"\n📂 Chargement des questions...")
    questions = load_questions()
    print(f"✅ {len(questions)} questions chargées")
    
    # Application
    applied = 0
    skipped = 0
    
    for i, correction in enumerate(auto_safe, 1):
        print(f"\n[{i}/{len(auto_safe)}] ", end='')
        
        if apply_correction(questions, correction, dry_run):
            applied += 1
        else:
            skipped += 1
    
    # Résumé
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}📈 RÉSULTAT")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Corrections appliquées: {applied}")
    print(f"Corrections sautées: {skipped}")
    
    if not dry_run and applied > 0:
        # Sauvegarde
        if confirm_action(f"Sauvegarder les modifications ?"):
            save_questions(questions, backup=True)
            print(f"\n✅ Corrections sauvegardées !")
            print(f"\n💡 Prochaines étapes:")
            print(f"   1. Rebuild: npm run build")
            print(f"   2. Test local: npm run dev")
            print(f"   3. Commit: git add -A && git commit -m 'fix: Corrections bugs batch'")
            print(f"   4. Deploy: vercel --prod")
        else:
            print(f"\n❌ Modifications annulées")

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Point d'entrée principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Application interactive des corrections de bugs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Mode interactif (recommandé)
  python apply_corrections.py
  
  # Dry-run (simulation)
  python apply_corrections.py --dry-run
  
  # Auto-safe uniquement
  python apply_corrections.py --auto-only

⚠️  IMPORTANT : Toujours faire un backup avant d'appliquer !
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Simule les corrections sans les appliquer')
    parser.add_argument('--auto-only', action='store_true',
                       help='Uniquement les corrections auto-safe (avec confirmation)')
    
    args = parser.parse_args()
    
    print("🔧 APPLICATION DES CORRECTIONS DE BUGS")
    print("=" * 50)
    
    if args.dry_run:
        print("⚠️  MODE DRY-RUN : Aucune modification ne sera appliquée")
    
    # Chargement corrections
    print(f"\n📂 Chargement des corrections...")
    corrections_data = load_corrections()
    
    # Mode interactif
    interactive_mode(corrections_data, dry_run=args.dry_run)

if __name__ == '__main__':
    main()

