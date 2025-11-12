#!/usr/bin/env python3
"""
Analyse automatique des rapports de bugs utilisateurs
Extraction depuis Redis → Analyse IA → Suggestions de correction

Usage:
    python scripts/bug_analysis/analyze_bug_reports.py
    python scripts/bug_analysis/analyze_bug_reports.py --auto-fix
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Any
import requests

# Ajouter le chemin parent pour imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# =============================================================================
# CONFIGURATION
# =============================================================================

# Redis Upstash (depuis .env.production)
REDIS_URL = os.getenv('KV_REST_API_URL', 'https://full-crab-26762.upstash.io')
REDIS_TOKEN = os.getenv('KV_REST_API_TOKEN')

# Fichiers de données
QUESTIONS_FILE = 'src/data/questions/compiled.json'
BUG_REPORTS_OUTPUT = 'reports/bug_reports_analysis.json'
CORRECTIONS_OUTPUT = 'reports/bug_corrections_proposed.json'

# Seuils de décision
CONFIDENCE_THRESHOLD = 0.7  # Confiance minimale pour auto-correction
MIN_REPORTS_SAME_ISSUE = 2  # Nombre minimum de rapports identiques

# =============================================================================
# HELPERS REDIS
# =============================================================================

def fetch_all_bug_reports() -> List[Dict[str, Any]]:
    """Récupère tous les rapports de bugs depuis Redis"""
    if not REDIS_TOKEN:
        print("⚠️  Variables Redis non configurées")
        return []
    
    try:
        response = requests.get(
            f"{REDIS_URL}/lrange/bug_reports:all/0/-1",
            headers={'Authorization': f'Bearer {REDIS_TOKEN}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get('result', [])
            print(f"✅ {len(reports)} rapports récupérés depuis Redis")
            return reports
        else:
            print(f"❌ Erreur Redis: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception Redis: {e}")
        return []

def fetch_bug_stats() -> Dict[str, int]:
    """Récupère les statistiques par catégorie"""
    if not REDIS_TOKEN:
        return {}
    
    try:
        response = requests.get(
            f"{REDIS_URL}/hgetall/bug_stats:categories",
            headers={'Authorization': f'Bearer {REDIS_TOKEN}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('result', {})
        else:
            return {}
    except Exception as e:
        print(f"⚠️  Erreur stats Redis: {e}")
        return {}

# =============================================================================
# ANALYSE DES RAPPORTS
# =============================================================================

def analyze_reports(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyse les rapports et génère des insights"""
    
    if not reports:
        return {
            'total_reports': 0,
            'by_category': {},
            'by_severity': {},
            'by_module': {},
            'most_reported_questions': [],
            'critical_issues': []
        }
    
    # Compteurs
    by_category = Counter()
    by_severity = Counter()
    by_module = Counter()
    by_question = defaultdict(list)
    
    for report in reports:
        by_category[report.get('category', 'unknown')] += 1
        by_severity[report.get('severity', 'unknown')] += 1
        
        context = report.get('context', {})
        by_module[context.get('moduleId', 'unknown')] += 1
        
        question_id = report.get('questionId')
        if question_id:
            by_question[question_id].append(report)
    
    # Questions les plus signalées
    most_reported = sorted(
        by_question.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:20]
    
    most_reported_questions = [
        {
            'question_id': q_id,
            'report_count': len(reports_list),
            'categories': list(set(r.get('category') for r in reports_list)),
            'severity_max': max((r.get('severity', 'low') for r in reports_list),
                               key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x, 0))
        }
        for q_id, reports_list in most_reported
    ]
    
    # Issues critiques (haute sévérité + multiples rapports)
    critical_issues = [
        {
            'question_id': q_id,
            'report_count': len(reports_list),
            'category': reports_list[0].get('category'),
            'descriptions': [r.get('description') for r in reports_list[:3]]
        }
        for q_id, reports_list in most_reported
        if len(reports_list) >= MIN_REPORTS_SAME_ISSUE and
           any(r.get('severity') == 'high' for r in reports_list)
    ]
    
    return {
        'total_reports': len(reports),
        'by_category': dict(by_category),
        'by_severity': dict(by_severity),
        'by_module': dict(by_module),
        'most_reported_questions': most_reported_questions,
        'critical_issues': critical_issues,
        'analysis_date': datetime.now().isoformat()
    }

# =============================================================================
# PROPOSITIONS DE CORRECTION
# =============================================================================

def load_questions() -> Dict[str, Any]:
    """Charge les questions depuis compiled.json"""
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data if isinstance(data, list) else data.get('questions', [])
            
            # Index par ID et chunk_id
            questions_by_id = {}
            for q in questions:
                q_id = q.get('id') or q.get('chunk_id')
                if q_id:
                    questions_by_id[q_id] = q
            
            return questions_by_id
    except Exception as e:
        print(f"❌ Erreur chargement questions: {e}")
        return {}

def propose_corrections(analysis: Dict[str, Any], questions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Propose des corrections basées sur les rapports"""
    
    corrections = []
    
    for issue in analysis.get('critical_issues', []):
        question_id = issue['question_id']
        question = questions.get(question_id)
        
        if not question:
            continue
        
        category = issue['category']
        
        # Génère une proposition de correction selon la catégorie
        correction = {
            'question_id': question_id,
            'current_question': {
                'text': question.get('text'),
                'options': question.get('options'),
                'correctAnswer': question.get('correctAnswer'),
                'explanation': question.get('explanation')
            },
            'issue_category': category,
            'report_count': issue['report_count'],
            'user_descriptions': issue['descriptions'],
            'proposed_action': get_proposed_action(category),
            'auto_fixable': is_auto_fixable(category),
            'confidence': calculate_confidence(issue),
            'priority': calculate_priority(issue),
            'timestamp': datetime.now().isoformat()
        }
        
        corrections.append(correction)
    
    # Tri par priorité
    corrections.sort(key=lambda x: x['priority'], reverse=True)
    
    return corrections

def get_proposed_action(category: str) -> str:
    """Retourne l'action recommandée selon la catégorie"""
    actions = {
        'reponse_incorrecte': 'Vérifier et corriger la réponse correcte',
        'plusieurs_reponses': 'Reformuler pour éliminer ambiguïté',
        'question_ambigue': 'Réécrire la question plus clairement',
        'explication_incorrecte': 'Corriger l\'explication biomédicale',
        'explication_manquante': 'Compléter l\'explication avec détails',
        'reference_incorrecte': 'Vérifier et corriger le lien vers le cours',
        'terme_medical_incorrect': 'Corriger le terme biomédical',
        'faute_orthographe': 'Corriger orthographe/grammaire',
        'options_repetees': 'Reformuler les options pour les différencier',
        'difficulte_mal_calibree': 'Réévaluer la difficulté',
        'hors_programme': 'Marquer pour suppression ou révision',
        'autre': 'Analyse manuelle requise'
    }
    return actions.get(category, 'Analyse manuelle requise')

def is_auto_fixable(category: str) -> bool:
    """Détermine si le bug peut être corrigé automatiquement"""
    auto_fixable = {
        'faute_orthographe': True,
        'reference_incorrecte': True,  # Si on a la bonne référence
        'difficulte_mal_calibree': True,
        'explication_manquante': False,  # Nécessite génération IA
        'reponse_incorrecte': False,     # Nécessite validation expert
        'terme_medical_incorrect': False,
        'question_ambigue': False,
        'plusieurs_reponses': False,
        'explication_incorrecte': False,
        'options_repetees': False,
        'hors_programme': False,
        'autre': False
    }
    return auto_fixable.get(category, False)

def calculate_confidence(issue: Dict[str, Any]) -> float:
    """Calcule le niveau de confiance pour la correction"""
    # Plus de rapports = plus de confiance
    report_count = issue['report_count']
    base_confidence = min(report_count / 5.0, 1.0)  # Max à 5 rapports
    
    # Ajuste selon la catégorie
    if issue['category'] in ['faute_orthographe', 'reference_incorrecte']:
        base_confidence *= 1.2  # Plus de confiance pour ces corrections simples
    
    return min(base_confidence, 1.0)

def calculate_priority(issue: Dict[str, Any]) -> int:
    """Calcule la priorité de correction (1-100)"""
    priority = issue['report_count'] * 10  # Base sur nombre de rapports
    
    # Bonus selon catégorie
    category_bonus = {
        'reponse_incorrecte': 50,
        'terme_medical_incorrect': 40,
        'explication_incorrecte': 30,
        'plusieurs_reponses': 25,
        'question_ambigue': 20,
        'reference_incorrecte': 15,
        'explication_manquante': 15,
        'options_repetees': 10,
        'faute_orthographe': 5,
        'difficulte_mal_calibree': 5,
        'hors_programme': 3,
        'autre': 1
    }
    
    priority += category_bonus.get(issue['category'], 0)
    
    return min(priority, 100)

# =============================================================================
# GÉNÉRATION RAPPORTS
# =============================================================================

def generate_report(analysis: Dict[str, Any], corrections: List[Dict[str, Any]]):
    """Génère les rapports d'analyse"""
    
    # Rapport d'analyse
    os.makedirs('reports', exist_ok=True)
    
    with open(BUG_REPORTS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Rapport d'analyse: {BUG_REPORTS_OUTPUT}")
    
    # Rapport de corrections
    with open(CORRECTIONS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({
            'corrections': corrections,
            'summary': {
                'total_corrections': len(corrections),
                'auto_fixable': sum(1 for c in corrections if c['auto_fixable']),
                'high_priority': sum(1 for c in corrections if c['priority'] >= 70),
                'high_confidence': sum(1 for c in corrections if c['confidence'] >= CONFIDENCE_THRESHOLD)
            },
            'generated_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Corrections proposées: {CORRECTIONS_OUTPUT}")
    
    # Affichage console
    print(f"\n📊 RÉSUMÉ ANALYSE")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total rapports: {analysis['total_reports']}")
    print(f"\nPar catégorie:")
    for cat, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {cat}: {count}")
    
    print(f"\nPar sévérité:")
    for sev, count in analysis['by_severity'].items():
        print(f"  • {sev}: {count}")
    
    print(f"\nQuestions les plus signalées: {len(analysis['most_reported_questions'])}")
    print(f"Issues critiques: {len(analysis['critical_issues'])}")
    
    print(f"\n🔧 CORRECTIONS PROPOSÉES")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total: {len(corrections)}")
    print(f"Auto-corrigeables: {sum(1 for c in corrections if c['auto_fixable'])}")
    print(f"Haute priorité (≥70): {sum(1 for c in corrections if c['priority'] >= 70)}")
    print(f"Haute confiance (≥{CONFIDENCE_THRESHOLD}): {sum(1 for c in corrections if c['confidence'] >= CONFIDENCE_THRESHOLD)}")
    
    if corrections:
        print(f"\nTop 5 corrections prioritaires:")
        for i, correction in enumerate(corrections[:5], 1):
            print(f"{i}. Question: {correction['question_id']}")
            print(f"   Catégorie: {correction['issue_category']}")
            print(f"   Priorité: {correction['priority']}")
            print(f"   Confiance: {correction['confidence']:.2f}")
            print(f"   Action: {correction['proposed_action']}")
            print()

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Point d'entrée principal"""
    print("🐛 ANALYSE DES RAPPORTS DE BUGS")
    print("=" * 50)
    
    # 1. Récupération des rapports
    print("\n1️⃣  Récupération des rapports depuis Redis...")
    reports = fetch_all_bug_reports()
    
    if not reports:
        print("⚠️  Aucun rapport à analyser")
        return
    
    # 2. Analyse
    print("\n2️⃣  Analyse des rapports...")
    analysis = analyze_reports(reports)
    
    # 3. Chargement questions
    print("\n3️⃣  Chargement des questions...")
    questions = load_questions()
    print(f"✅ {len(questions)} questions chargées")
    
    # 4. Propositions de correction
    print("\n4️⃣  Génération des propositions de correction...")
    corrections = propose_corrections(analysis, questions)
    
    # 5. Génération rapports
    print("\n5️⃣  Génération des rapports...")
    generate_report(analysis, corrections)
    
    print(f"\n✅ Analyse terminée !")
    print(f"\n💡 Prochaines étapes:")
    print(f"   1. Examiner: {CORRECTIONS_OUTPUT}")
    print(f"   2. Appliquer corrections auto: python scripts/bug_analysis/apply_corrections.py")
    print(f"   3. Réviser manuellement les corrections complexes")

if __name__ == '__main__':
    main()

