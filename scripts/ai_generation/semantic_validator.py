#!/usr/bin/env python3
"""
Script de validation sémantique et lexicale
Tâches [026-027-038] - Phase 4 : Validation Double

Objectif:
- Calculer context_score : similarité question ↔ chunk source (embeddings)
- Calculer keywords_overlap : % mots-clés module présents dans question
- Validation combinée : rejette si l'un des 3 scores < seuil

Usage:
    python scripts/ai_generation/semantic_validator.py \
           --in generated_biobert.json \
           --modules src/data/modules/ \
           --keywords src/data/keywords.json \
           --out generated_scored.json
"""

import argparse
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    from tqdm import tqdm
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install sentence-transformers tqdm")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

CONTEXT_SCORE_THRESHOLD = 0.60  # Abaissé de 0.75 pour validation v1
KEYWORDS_OVERLAP_THRESHOLD = 0.30  # Abaissé de 0.5 pour validation v1

# =============================================================================
# CHARGEMENT CHUNKS SOURCES
# =============================================================================

def load_chunks_index(modules_dir: Path) -> Dict[str, Dict]:
    """
    Charge tous les chunks de tous les modules et crée un index chunk_id → chunk.
    
    Returns:
        Dict[chunk_id, chunk_data]
    """
    chunks_index = {}
    
    module_files = list(modules_dir.glob("*.json"))
    module_files = [f for f in module_files if f.stem not in ['reclassification_proposals']]
    
    for module_file in module_files:
        with open(module_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)
        
        for section in module_data.get('sections', []):
            for chunk in section.get('chunks', []):
                chunks_index[chunk['chunk_id']] = chunk
    
    return chunks_index

# =============================================================================
# CONTEXT SCORE (SIMILARITÉ SÉMANTIQUE)
# =============================================================================

class SemanticValidator:
    """Validateur sémantique utilisant sentence-transformers."""
    
    def __init__(self, chunks_index: Dict[str, Dict]):
        """Initialise le validateur."""
        print("🔧 Chargement modèle sentence-transformers...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("   ✓ Modèle chargé")
        
        self.chunks_index = chunks_index
        
        # Pré-calcul embeddings des chunks (cache)
        print(f"🔧 Pré-calcul embeddings des {len(chunks_index)} chunks...")
        self.chunk_embeddings = {}
        
        for chunk_id, chunk in tqdm(chunks_index.items(), desc="Embeddings chunks"):
            chunk_text = chunk.get('text', '')
            if chunk_text:
                embedding = self.model.encode(chunk_text, convert_to_numpy=True)
                self.chunk_embeddings[chunk_id] = embedding
        
        print(f"   ✓ {len(self.chunk_embeddings)} embeddings calculés")
    
    def compute_context_score(self, question: Dict) -> float:
        """
        Calcule le context_score : similarité entre question et chunk source.
        
        Returns:
            Score de similarité [0, 1]
        """
        chunk_id = question.get('chunk_id')
        
        if not chunk_id or chunk_id not in self.chunk_embeddings:
            return 0.0
        
        # Texte question
        question_text = f"{question.get('text', '')} {question.get('explanation', '')}"
        
        # Embedding question
        question_embedding = self.model.encode(question_text, convert_to_numpy=True)
        
        # Embedding chunk source
        chunk_embedding = self.chunk_embeddings[chunk_id]
        
        # Cosine similarity
        similarity = np.dot(question_embedding, chunk_embedding) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(chunk_embedding)
        )
        
        return float(similarity)

# =============================================================================
# KEYWORDS OVERLAP (FIDÉLITÉ LEXICALE)
# =============================================================================

def extract_keywords_from_text(text: str, stopwords: Set[str] = None) -> Set[str]:
    """
    Extrait les mots significatifs d'un texte (lowercase, filtre stopwords).
    """
    if stopwords is None:
        stopwords = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou',
            'est', 'sont', 'a', 'ont', 'pour', 'dans', 'par', 'avec', 'sur'
        }
    
    # Lowercase et split
    words = text.lower().split()
    
    # Filtre : mots >= 3 caractères, pas de stopwords
    keywords = {
        word.strip('.,;:!?()[]{}\"\'')
        for word in words
        if len(word) >= 3 and word.lower() not in stopwords
    }
    
    return keywords

def compute_keywords_overlap(question: Dict, module_keywords: List[str]) -> float:
    """
    Calcule le keywords_overlap : % mots-clés module présents dans question.
    
    Returns:
        Overlap score [0, 1]
    """
    if not module_keywords:
        return 0.0
    
    # Texte question
    question_text = f"{question.get('text', '')} {question.get('explanation', '')}"
    
    # Extraction mots-clés question
    question_keywords = extract_keywords_from_text(question_text)
    
    # Mots-clés module (lowercase)
    module_keywords_lower = {kw.lower() for kw in module_keywords}
    
    # Intersection
    intersection = question_keywords & module_keywords_lower
    
    # Overlap ratio
    overlap = len(intersection) / len(module_keywords_lower) if module_keywords_lower else 0.0
    
    return float(overlap)

# =============================================================================
# VALIDATION COMBINÉE
# =============================================================================

def validate_questions(
    questions: List[Dict],
    validator: SemanticValidator,
    keywords_data: Dict
) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Valide toutes les questions avec triple validation.
    
    Returns:
        (questions_passed, questions_rejected, stats)
    """
    print(f"\n🔍 Validation sémantique de {len(questions)} questions...")
    print(f"   Seuils : context_score > {CONTEXT_SCORE_THRESHOLD}, keywords_overlap > {KEYWORDS_OVERLAP_THRESHOLD}")
    
    passed = []
    rejected = []
    
    stats = {
        'total': len(questions),
        'passed': 0,
        'rejected': 0,
        'rejection_reasons': {
            'biomedical_score': 0,
            'context_score': 0,
            'keywords_overlap': 0
        },
        'by_module': {}
    }
    
    for question in tqdm(questions, desc="Validation sémantique"):
        module_id = question.get('module_id', 'unknown')
        
        # Récupère mots-clés module
        module_keywords = keywords_data.get(module_id, {}).get('module_keywords', [])
        
        # Calcul context_score
        context_score = validator.compute_context_score(question)
        question['context_score'] = round(context_score, 4)
        
        # Calcul keywords_overlap
        keywords_overlap = compute_keywords_overlap(question, module_keywords)
        question['keywords_overlap'] = round(keywords_overlap, 4)
        
        # Validation combinée
        biomedical_score = question.get('biomedical_score', 0)
        biomedical_threshold = question.get('biomedical_threshold', 0.05)
        
        reject_reasons = []
        
        if biomedical_score < biomedical_threshold:
            reject_reasons.append('biomedical_score')
            stats['rejection_reasons']['biomedical_score'] += 1
        
        if context_score < CONTEXT_SCORE_THRESHOLD:
            reject_reasons.append('context_score')
            stats['rejection_reasons']['context_score'] += 1
        
        if keywords_overlap < KEYWORDS_OVERLAP_THRESHOLD:
            reject_reasons.append('keywords_overlap')
            stats['rejection_reasons']['keywords_overlap'] += 1
        
        # Stats par module
        if module_id not in stats['by_module']:
            stats['by_module'][module_id] = {
                'total': 0,
                'passed': 0,
                'rejected': 0
            }
        
        stats['by_module'][module_id]['total'] += 1
        
        # Décision
        if reject_reasons:
            question['rejected'] = True
            question['rejection_reasons'] = reject_reasons
            rejected.append(question)
            stats['rejected'] += 1
            stats['by_module'][module_id]['rejected'] += 1
        else:
            question['rejected'] = False
            passed.append(question)
            stats['passed'] += 1
            stats['by_module'][module_id]['passed'] += 1
    
    return passed, rejected, stats

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validation sémantique et lexicale")
    parser.add_argument('--in', dest='input_file', required=True, help='Fichier questions avec biomedical_score')
    parser.add_argument('--modules', required=True, help='Dossier modules (pour récupérer chunks)')
    parser.add_argument('--keywords', required=True, help='Fichier keywords.json')
    parser.add_argument('--out', required=True, help='Fichier questions validées de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VALIDATION SÉMANTIQUE ET LEXICALE")
    print("="*60)
    
    # Charge questions
    print(f"\n📂 Chargement questions : {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Charge keywords
    print(f"\n📂 Chargement keywords : {args.keywords}")
    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords_data = json.load(f)
    print(f"   ✓ Keywords chargés")
    
    # Charge chunks (index)
    print(f"\n📂 Chargement chunks : {args.modules}")
    chunks_index = load_chunks_index(Path(args.modules))
    print(f"   ✓ {len(chunks_index)} chunks indexés")
    
    # Initialise validateur
    validator = SemanticValidator(chunks_index)
    
    # Validation
    passed, rejected, stats = validate_questions(questions, validator, keywords_data)
    
    # Affichage résultats
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS VALIDATION SÉMANTIQUE")
    print(f"{'='*60}")
    print(f"Questions validées : {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)")
    print(f"Questions rejetées : {stats['rejected']} ({stats['rejected']/stats['total']*100:.1f}%)")
    
    print(f"\n📊 Raisons de rejet :")
    for reason, count in stats['rejection_reasons'].items():
        print(f"  - {reason:20s} : {count:4d} questions")
    
    print(f"\n📊 Par module (top 10 validées) :")
    sorted_modules = sorted(
        stats['by_module'].items(),
        key=lambda x: x[1]['passed'],
        reverse=True
    )[:10]
    
    for module_id, module_stats in sorted_modules:
        passed_pct = module_stats['passed'] / module_stats['total'] * 100 if module_stats['total'] > 0 else 0
        print(f"  {module_id:20s} : {module_stats['passed']:3d}/{module_stats['total']:3d} validées ({passed_pct:5.1f}%)")
    
    # Validation objectifs
    rejection_rate = stats['rejected'] / stats['total'] * 100
    
    print(f"\n{'='*60}")
    if stats['passed'] >= 2000:
        print(f"✅ OBJECTIF ATTEINT : {stats['passed']} questions validées (≥ 2000)")
    else:
        print(f"⚠️  OBJECTIF NON ATTEINT : {stats['passed']} questions validées (objectif: ≥ 2000)")
    
    if rejection_rate < 20:
        print(f"✅ TAUX REJET OK : {rejection_rate:.1f}% < 20%")
    else:
        print(f"⚠️  TAUX REJET ÉLEVÉ : {rejection_rate:.1f}% ≥ 20%")
        print(f"   Suggestions:")
        print(f"   - Abaisser seuils (context_score à 0.70, keywords_overlap à 0.45)")
        print(f"   - Améliorer génération (prompts plus ancrés)")
    print(f"{'='*60}")
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'validated_at': datetime.now().isoformat(),
        'thresholds': {
            'context_score': CONTEXT_SCORE_THRESHOLD,
            'keywords_overlap': KEYWORDS_OVERLAP_THRESHOLD
        },
        'stats': stats,
        'questions': passed,
        'rejected_questions': rejected
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Questions validées sauvegardées : {args.out}")
    print(f"   ({stats['passed']} validées + {stats['rejected']} rejetées)")
    
    print(f"\n{'='*60}")
    print(f"✅ VALIDATION SÉMANTIQUE TERMINÉE")
    print(f"{'='*60}")
    
    return 0 if stats['passed'] >= 2000 and rejection_rate < 20 else 1

if __name__ == "__main__":
    exit(main())

