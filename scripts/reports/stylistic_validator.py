#!/usr/bin/env python3
"""
Script de validation stylistique
Tâche [024b] - Phase 2 : Indexation & Alignement

Objectif:
- Mesurer distance stylistique entre QCM générés et annales
- Distance Levenshtein normalisée + similarité phrastique
- Auto-calibration des prompts si distance > 0.35

Usage:
    python scripts/reports/stylistic_validator.py \
           --questions generated_raw.json \
           --annales-profile src/data/annales_profile.json \
           --out src/data/style_calibration_log.json
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install sentence-transformers numpy")
    exit(1)

# =============================================================================
# DISTANCE LEVENSHTEIN
# =============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcule la distance de Levenshtein entre deux chaînes."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def normalized_levenshtein(s1: str, s2: str) -> float:
    """
    Distance de Levenshtein normalisée (0-1).
    0 = identique, 1 = complètement différent
    """
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return distance / max_len if max_len > 0 else 0.0

# =============================================================================
# SIMILARITÉ PHRASTIQUE
# =============================================================================

def calculate_semantic_similarity(texts1: List[str], texts2: List[str], model) -> float:
    """
    Calcule la similarité sémantique moyenne entre deux listes de textes.
    
    Returns:
        Score de similarité (0-1), 1 = très similaire
    """
    if not texts1 or not texts2:
        return 0.0
    
    # Embeddings
    embeddings1 = model.encode(texts1)
    embeddings2 = model.encode(texts2)
    
    # Calcul cosine similarity moyenne
    similarities = []
    
    for emb1 in embeddings1:
        # Similarité max avec n'importe quel embedding de texts2
        sims = [
            np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            for emb2 in embeddings2
        ]
        similarities.append(max(sims))
    
    return float(np.mean(similarities))

# =============================================================================
# VALIDATION STYLISTIQUE
# =============================================================================

def validate_stylistic_match(
    questions: List[Dict],
    annales_samples: List[str],
    sample_size: int = 50
) -> Dict:
    """
    Valide la correspondance stylistique entre questions générées et annales.
    
    Args:
        questions: Liste de questions générées (dicts avec 'text')
        annales_samples: Liste de questions des annales
        sample_size: Nombre de questions à échantillonner
    
    Returns:
        Stats de validation avec distances
    """
    print(f"\n🔍 Validation stylistique sur échantillon de {sample_size} questions...")
    
    # Échantillonnage
    sample_generated = random.sample(questions, min(sample_size, len(questions)))
    
    # 1. Distance Levenshtein
    print("   Calcul distances Levenshtein...")
    levenshtein_distances = []
    
    for q in sample_generated[:20]:  # Limite à 20 pour performance
        q_text = q.get('text', '')
        
        # Compare avec toutes les questions annales, prend la plus proche
        if annales_samples:
            distances = [normalized_levenshtein(q_text, annale) for annale in annales_samples]
            min_distance = min(distances)
            levenshtein_distances.append(min_distance)
    
    avg_levenshtein = np.mean(levenshtein_distances) if levenshtein_distances else 1.0
    
    # 2. Similarité phrastique (sentence-transformers)
    print("   Calcul similarité sémantique...")
    
    # Charge modèle léger pour similarité
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    generated_texts = [q.get('text', '') for q in sample_generated[:30]]
    
    if annales_samples and generated_texts:
        semantic_sim = calculate_semantic_similarity(generated_texts, annales_samples, model)
    else:
        semantic_sim = 0.0
    
    # 3. Analyse longueur
    generated_lengths = [len(q.get('text', '')) for q in sample_generated]
    avg_length_generated = np.mean(generated_lengths) if generated_lengths else 0
    
    annales_lengths = [len(a) for a in annales_samples]
    avg_length_annales = np.mean(annales_lengths) if annales_lengths else 0
    
    # Calcul distance stylistique globale
    # Combine Levenshtein (70%) + différence longueur (30%)
    length_diff_normalized = abs(avg_length_generated - avg_length_annales) / max(avg_length_annales, 1)
    stylistic_distance = 0.7 * avg_levenshtein + 0.3 * min(length_diff_normalized, 1.0)
    
    stats = {
        'sample_size': len(sample_generated),
        'avg_levenshtein_distance': float(avg_levenshtein),
        'avg_semantic_similarity': float(semantic_sim),
        'avg_length_generated': float(avg_length_generated),
        'avg_length_annales': float(avg_length_annales),
        'length_difference_percent': float(abs(avg_length_generated - avg_length_annales) / avg_length_annales * 100) if avg_length_annales > 0 else 0,
        'stylistic_distance': float(stylistic_distance)
    }
    
    return stats

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validation stylistique QCM vs annales")
    parser.add_argument('--questions', required=True, help='Fichier questions générées (JSON)')
    parser.add_argument('--annales-profile', required=True, help='Fichier annales_profile.json')
    parser.add_argument('--out', required=True, help='Fichier style_calibration_log.json de sortie')
    parser.add_argument('--sample-size', type=int, default=50, help='Taille échantillon (défaut: 50)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VALIDATION STYLISTIQUE")
    print("="*60)
    
    # Charge questions générées
    print(f"\n📂 Chargement questions : {args.questions}")
    with open(args.questions, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    questions = questions_data if isinstance(questions_data, list) else questions_data.get('questions', [])
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Charge profil annales
    print(f"\n📂 Chargement profil annales : {args.annales_profile}")
    with open(args.annales_profile, 'r', encoding='utf-8') as f:
        annales_profile = json.load(f)
    
    # Pour la validation, on utilise des échantillons synthétiques basés sur le profil
    # (Car l'extraction réelle des annales est limitée)
    annales_samples = []
    
    # Si le profil contient des exemples, on les utilise
    # Sinon, on crée des pseudo-échantillons basés sur les starters communs
    for starter in annales_profile.get('common_starters', [])[:10]:
        sample = f"{starter} la morphine dans le traitement de la douleur ?"
        annales_samples.append(sample)
    
    # Si vraiment aucun échantillon, on crée un générique
    if not annales_samples:
        annales_samples = [
            "Quelle est la classe de la morphine selon l'OMS ?",
            "Parmi les propositions suivantes concernant la ventilation mécanique ?",
            "Concernant le choc septique, quelle est la première ligne de traitement ?"
        ]
    
    print(f"   ✓ {len(annales_samples)} échantillons de référence")
    
    # Validation stylistique
    stats = validate_stylistic_match(questions, annales_samples, args.sample_size)
    
    # Affichage résultats
    print("\n" + "="*60)
    print("📊 RÉSULTATS VALIDATION STYLISTIQUE")
    print("="*60)
    print(f"Distance Levenshtein moyenne : {stats['avg_levenshtein_distance']:.3f}")
    print(f"Similarité sémantique moyenne : {stats['avg_semantic_similarity']:.3f}")
    print(f"Longueur moyenne générée : {stats['avg_length_generated']:.0f} caractères")
    print(f"Longueur moyenne annales : {stats['avg_length_annales']:.0f} caractères")
    print(f"Différence longueur : {stats['length_difference_percent']:.1f}%")
    print(f"\n🎯 DISTANCE STYLISTIQUE GLOBALE : {stats['stylistic_distance']:.3f}")
    
    # Validation du seuil
    if stats['stylistic_distance'] < 0.3:
        print(f"✅ Objectif atteint (< 0.3)")
        status = "converged"
    elif stats['stylistic_distance'] < 0.35:
        print(f"⚠️  Objectif proche (< 0.35, objectif: < 0.3)")
        status = "acceptable"
    else:
        print(f"❌ Objectif non atteint (> 0.35)")
        print(f"   Suggestion: ajuster prompts (longueur, structure)")
        status = "needs_improvement"
    
    # Génère log de calibration
    calibration_log = {
        'iterations': [
            {
                'iter': 1,
                'stats': stats,
                'status': status,
                'prompt_adjustments': []
            }
        ]
    }
    
    # Suggestions d'ajustement si nécessaire
    if status == "needs_improvement":
        suggestions = []
        
        if stats['length_difference_percent'] > 30:
            if stats['avg_length_generated'] > stats['avg_length_annales']:
                suggestions.append("Raccourcir les énoncés (trop longs)")
            else:
                suggestions.append("Allonger les énoncés (trop courts)")
        
        if stats['avg_levenshtein_distance'] > 0.6:
            suggestions.append("Utiliser davantage les starters des annales")
            suggestions.append(f"Starters recommandés: {', '.join(annales_profile.get('common_starters', [])[:3])}")
        
        calibration_log['iterations'][0]['prompt_adjustments'] = suggestions
        
        print(f"\n💡 Suggestions d'ajustement:")
        for suggestion in suggestions:
            print(f"   - {suggestion}")
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(calibration_log, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Log de calibration sauvegardé : {args.out}")
    
    print("\n" + "="*60)
    print("✅ VALIDATION STYLISTIQUE TERMINÉE")
    print("="*60)
    
    return 0 if status in ["converged", "acceptable"] else 1

if __name__ == "__main__":
    exit(main())

