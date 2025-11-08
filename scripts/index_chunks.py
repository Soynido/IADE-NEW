#!/usr/bin/env python3
"""
Script d'indexation TF-IDF des chunks
Tâche [018] - Phase 2 : Indexation & Alignement

Objectif:
- Extraire les mots-clés dominants de chaque chunk via TF-IDF
- Agréger par module pour créer keywords.json
- Sert de base pour le contrôle lexical de la génération

Usage:
    python scripts/index_chunks.py --modules src/data/modules/ \
                                   --out src/data/keywords.json
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install scikit-learn numpy")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Stopwords médicaux français (à ne pas considérer comme mots-clés)
MEDICAL_STOPWORDS = [
    "patient", "patients", "cas", "être", "fait", "permet", "doit", "peut",
    "fois", "niveau", "présence", "absence", "ainsi", "donc", "notamment",
    "par", "pour", "avec", "dans", "sur", "lors", "selon", "via"
]

TOP_N_KEYWORDS_PER_CHUNK = 10
TOP_N_KEYWORDS_PER_MODULE = 50

# =============================================================================
# FONCTIONS
# =============================================================================

def extract_keywords_tfidf(texts: List[str], top_n: int = 10) -> List[List[str]]:
    """
    Extrait les top N mots-clés de chaque texte via TF-IDF.
    
    Args:
        texts: Liste de textes (chunks)
        top_n: Nombre de mots-clés à extraire par texte
    
    Returns:
        Liste de listes de mots-clés (une liste par texte)
    """
    if not texts:
        return []
    
    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),  # Unigrammes et bigrammes
        stop_words=MEDICAL_STOPWORDS,
        lowercase=True,
        min_df=1,
        max_df=0.8
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        keywords_per_text = []
        
        for i, text in enumerate(texts):
            # Récupère les scores TF-IDF pour ce texte
            scores = tfidf_matrix[i].toarray()[0]
            
            # Trie les indices par score décroissant
            top_indices = np.argsort(scores)[::-1][:top_n]
            
            # Récupère les mots-clés correspondants
            keywords = [feature_names[idx] for idx in top_indices if scores[idx] > 0]
            keywords_per_text.append(keywords)
        
        return keywords_per_text
        
    except Exception as e:
        print(f"⚠️  Erreur TF-IDF: {e}")
        return [[] for _ in texts]

def index_module(module_data: Dict, module_id: str) -> Dict:
    """
    Indexe un module complet : extrait mots-clés par chunk et agrège.
    
    Returns:
        {
            'module_id': str,
            'chunk_keywords': {chunk_id: [keywords]},
            'module_keywords': [top keywords],
            'chunks_count': int
        }
    """
    chunks = []
    chunk_ids = []
    
    # Collecte tous les chunks du module
    for section in module_data.get('sections', []):
        for chunk in section.get('chunks', []):
            chunks.append(chunk['text'])
            chunk_ids.append(chunk['chunk_id'])
    
    if not chunks:
        return {
            'module_id': module_id,
            'chunk_keywords': {},
            'module_keywords': [],
            'chunks_count': 0
        }
    
    # Extraction TF-IDF par chunk
    keywords_lists = extract_keywords_tfidf(chunks, TOP_N_KEYWORDS_PER_CHUNK)
    
    # Mapping chunk_id → keywords
    chunk_keywords = {
        chunk_id: keywords
        for chunk_id, keywords in zip(chunk_ids, keywords_lists)
    }
    
    # Agrégation module: top mots-clés les plus fréquents
    all_keywords = [kw for keywords in keywords_lists for kw in keywords]
    keyword_counts = Counter(all_keywords)
    module_keywords = [kw for kw, _ in keyword_counts.most_common(TOP_N_KEYWORDS_PER_MODULE)]
    
    return {
        'module_id': module_id,
        'chunk_keywords': chunk_keywords,
        'module_keywords': module_keywords,
        'chunks_count': len(chunks)
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Indexation TF-IDF des chunks")
    parser.add_argument('--modules', required=True, help='Dossier contenant les modules JSON')
    parser.add_argument('--out', required=True, help='Fichier keywords.json de sortie')
    
    args = parser.parse_args()
    
    print("="*60)
    print("INDEXATION TF-IDF DES CHUNKS")
    print("="*60)
    
    modules_dir = Path(args.modules)
    
    # Trouve tous les modules
    module_files = list(modules_dir.glob("*.json"))
    module_files = [f for f in module_files if f.stem != 'reclassification_proposals']
    
    print(f"\n📁 {len(module_files)} modules trouvés")
    
    # Indexation de chaque module
    indexed_modules = {}
    total_chunks_indexed = 0
    total_chunks_with_keywords = 0
    
    for module_file in sorted(module_files):
        module_id = module_file.stem
        
        with open(module_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)
        
        print(f"\n📊 Indexation module: {module_id}")
        indexed = index_module(module_data, module_id)
        
        if indexed['chunks_count'] == 0:
            print(f"   ⚠️  Module vide, skip")
            continue
        
        indexed_modules[module_id] = indexed
        
        chunks_with_kw = sum(1 for kws in indexed['chunk_keywords'].values() if len(kws) >= 3)
        total_chunks_indexed += indexed['chunks_count']
        total_chunks_with_keywords += chunks_with_kw
        
        coverage_percent = (chunks_with_kw / indexed['chunks_count'] * 100) if indexed['chunks_count'] > 0 else 0
        
        print(f"   ✓ {indexed['chunks_count']} chunks indexés")
        print(f"   ✓ {len(indexed['module_keywords'])} mots-clés module")
        print(f"   ✓ {chunks_with_kw}/{indexed['chunks_count']} chunks avec ≥3 mots-clés ({coverage_percent:.1f}%)")
        
        # Affiche top 10 mots-clés du module
        if indexed['module_keywords'][:10]:
            print(f"   Top mots-clés: {', '.join(indexed['module_keywords'][:10])}")
    
    # Stats globales
    global_coverage = (total_chunks_with_keywords / total_chunks_indexed * 100) if total_chunks_indexed > 0 else 0
    
    print("\n" + "="*60)
    print("📊 STATISTIQUES GLOBALES")
    print("="*60)
    print(f"Modules indexés : {len(indexed_modules)}")
    print(f"Chunks indexés : {total_chunks_indexed}")
    print(f"Chunks avec ≥3 mots-clés : {total_chunks_with_keywords} ({global_coverage:.1f}%)")
    
    # Validation du seuil
    if global_coverage >= 80:
        print(f"✅ Objectif atteint (≥80% chunks avec ≥3 mots-clés)")
    else:
        print(f"⚠️  Objectif non atteint : {global_coverage:.1f}% < 80%")
        print(f"   Suggestion: ajuster stopwords ou ngram_range")
    
    # Sauvegarde keywords.json
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(indexed_modules, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Mots-clés sauvegardés : {args.out}")
    
    print("\n" + "="*60)
    print("✅ INDEXATION TERMINÉE")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())

