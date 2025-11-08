#!/usr/bin/env python3
"""
Script de validation biomédicale via BioBERT
Tâches [030-031b] - Phase 4 : Validation Double

Objectif:
- Calculer embeddings BioBERT pour questions + explications
- Comparer avec centroïdes biomédicaux par module
- Appliquer seuils adaptatifs (0.05-0.10 selon module)
- Filtrer questions non biomédicalement cohérentes

Usage:
    python scripts/ai_generation/biobert_client.py \
           --in generated_raw.json \
           --out generated_biobert.json \
           --metadata src/data/metadata.json
"""

import argparse
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    from tqdm import tqdm
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install transformers torch tqdm")
    exit(1)

# =============================================================================
# SEED SENTENCES BIOMÉDICALES (centroïdes par module)
# =============================================================================

BIOMEDICAL_SEEDS = {
    "bases_physio": [
        "La cellule est l'unité fonctionnelle de l'organisme.",
        "L'homéostasie maintient l'équilibre interne.",
        "Le pH sanguin normal est de 7.35 à 7.45."
    ],
    "respiratoire": [
        "La PEEP améliore l'oxygénation en ventilation mécanique.",
        "Le rapport PaO2/FiO2 évalue la fonction respiratoire.",
        "La capnographie mesure l'EtCO2 expiré."
    ],
    "cardio": [
        "Le débit cardiaque est le produit de la fréquence par le volume d'éjection.",
        "La pression artérielle moyenne dépend du débit et des résistances vasculaires.",
        "Le choc septique nécessite un remplissage vasculaire et des vasopresseurs."
    ],
    "neuro": [
        "La pression intracrânienne normale est inférieure à 15 mmHg.",
        "Le score de Glasgow évalue le niveau de conscience.",
        "La pression de perfusion cérébrale doit être maintenue au-dessus de 60 mmHg."
    ],
    "pharma_generaux": [
        "Le propofol est un agent anesthésique intraveineux à action rapide.",
        "L'étomidate est indiqué en cas d'instabilité hémodynamique.",
        "La kétamine préserve le réflexe laryngé et la ventilation spontanée."
    ],
    "pharma_locaux": [
        "La lidocaïne est un anesthésique local de type amide.",
        "La bupivacaïne a une durée d'action prolongée.",
        "La toxicité des anesthésiques locaux se manifeste par des signes neurologiques puis cardiovasculaires."
    ],
    "pharma_opioides": [
        "La morphine est un opioïde fort de palier 3 selon l'OMS.",
        "Le fentanyl est un opioïde synthétique à action rapide.",
        "La naloxone est l'antidote des opioïdes."
    ],
    "pharma_curares": [
        "Le rocuronium est un curare non dépolarisant à action intermédiaire.",
        "Le sugammadex antagonise spécifiquement les curares aminostéroïdiens.",
        "La décurarisation nécessite la récupération du bloc neuromusculaire."
    ],
    "alr": [
        "La rachianesthésie produit un bloc sensitif, moteur et sympathique.",
        "La péridurale permet une analgésie prolongée.",
        "Les blocs nerveux périphériques ciblent les plexus et nerfs."
    ],
    "ventilation": [
        "L'intubation orotrachéale sécurise les voies aériennes.",
        "Le masque laryngé est une alternative à l'intubation.",
        "La capnographie confirme l'intubation trachéale."
    ],
    "transfusion": [
        "Les culots globulaires rouges augmentent la capacité de transport en oxygène.",
        "Le plasma frais congelé apporte des facteurs de coagulation.",
        "Le ROTEM évalue l'hémostase en temps réel."
    ],
    "reanimation": [
        "Le sepsis est une défaillance d'organe secondaire à une infection.",
        "Le SDRA se définit par un rapport PaO2/FiO2 inférieur à 300.",
        "Le polytrauma nécessite une prise en charge multidisciplinaire."
    ],
    "douleur": [
        "L'échelle visuelle analogique évalue l'intensité douloureuse.",
        "La PCA permet au patient de gérer son analgésie.",
        "Les antalgiques sont classés en 3 paliers selon l'OMS."
    ],
    "infectio": [
        "L'antibioprophylaxie prévient les infections du site opératoire.",
        "L'asepsie chirurgicale réduit la contamination microbienne.",
        "La préparation cutanée doit être rigoureuse."
    ],
    "monitorage": [
        "La SpO2 mesure la saturation en oxygène par photopléthysmographie.",
        "Le BIS quantifie la profondeur de l'anesthésie.",
        "La pression artérielle invasive permet un monitoring continu."
    ],
    "pediatrie": [
        "Les enfants ont des besoins pharmacologiques spécifiques.",
        "Les personnes âgées présentent une polypathologie.",
        "La grossesse modifie la pharmacocinétique des médicaments."
    ],
    "legislation": [
        "Le consentement éclairé est obligatoire avant tout acte anesthésique.",
        "La traçabilité des actes est une obligation réglementaire.",
        "La vigilance sanitaire signale les événements indésirables."
    ],
    "unknown": [
        "L'anesthésie-réanimation est une spécialité médicale.",
        "La formation IADE dure 24 mois.",
        "La pratique professionnelle suit des recommandations."
    ]
}

# =============================================================================
# BIOBERT EMBEDDINGS
# =============================================================================

class BioBERTScorer:
    """Client BioBERT pour calcul de scores biomédicaux."""
    
    def __init__(self):
        """Initialise le modèle BioBERT."""
        print("🔧 Chargement BioBERT...")
        self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
        self.model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
        self.model.eval()  # Mode évaluation
        print("   ✓ BioBERT chargé")
        
        # Pré-calcul des centroïdes par module
        print("🔧 Calcul des centroïdes biomédicaux par module...")
        self.centroids = self._compute_centroids()
        print(f"   ✓ {len(self.centroids)} centroïdes calculés")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Calcule l'embedding BioBERT d'un texte."""
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # CLS token embedding
        embedding = outputs.last_hidden_state[:, 0, :].numpy().flatten()
        return embedding
    
    def _compute_centroids(self) -> Dict[str, np.ndarray]:
        """Calcule les centroïdes (embeddings moyens) pour chaque module."""
        centroids = {}
        
        for module_id, seeds in BIOMEDICAL_SEEDS.items():
            embeddings = [self._get_embedding(seed) for seed in seeds]
            centroid = np.mean(embeddings, axis=0)
            centroids[module_id] = centroid
        
        return centroids
    
    def compute_biomedical_score(self, text: str, module_id: str) -> float:
        """
        Calcule le score biomédical d'un texte par rapport au module.
        
        Args:
            text: Texte à scorer (question + explanation)
            module_id: ID du module pour sélectionner le centroïde
        
        Returns:
            Score de similarité cosinus [0, 1]
        """
        # Embedding du texte
        text_embedding = self._get_embedding(text)
        
        # Centroïde du module (fallback sur 'unknown' si module non trouvé)
        centroid = self.centroids.get(module_id, self.centroids.get('unknown'))
        
        # Cosine similarity
        similarity = np.dot(text_embedding, centroid) / (
            np.linalg.norm(text_embedding) * np.linalg.norm(centroid)
        )
        
        return float(similarity)

# =============================================================================
# VALIDATION BIOMÉDICALE
# =============================================================================

def score_questions(
    questions: List[Dict],
    scorer: BioBERTScorer,
    thresholds: Dict[str, float]
) -> Tuple[List[Dict], Dict]:
    """
    Score toutes les questions avec BioBERT.
    
    Returns:
        (questions_scored, stats)
    """
    print(f"\n🧪 Scoring biomédical de {len(questions)} questions...")
    
    scored_questions = []
    stats = {
        'total': len(questions),
        'scored': 0,
        'passed': 0,
        'rejected': 0,
        'by_module': {}
    }
    
    for question in tqdm(questions, desc="Scoring BioBERT"):
        module_id = question.get('module_id', 'unknown')
        
        # Texte à scorer : question + explication
        text_to_score = f"{question.get('text', '')} {question.get('explanation', '')}"
        
        # Calcul score
        score = scorer.compute_biomedical_score(text_to_score, module_id)
        
        # Récupère seuil pour ce module
        threshold = thresholds.get(module_id, 0.05)
        
        # Enrichissement question
        question['biomedical_score'] = round(score, 4)
        question['biomedical_threshold'] = threshold
        
        scored_questions.append(question)
        stats['scored'] += 1
        
        # Stats par module
        if module_id not in stats['by_module']:
            stats['by_module'][module_id] = {
                'total': 0,
                'passed': 0,
                'rejected': 0,
                'avg_score': []
            }
        
        stats['by_module'][module_id]['total'] += 1
        stats['by_module'][module_id]['avg_score'].append(score)
        
        if score >= threshold:
            stats['passed'] += 1
            stats['by_module'][module_id]['passed'] += 1
        else:
            stats['rejected'] += 1
            stats['by_module'][module_id]['rejected'] += 1
    
    # Calcul moyennes par module
    for module_stats in stats['by_module'].values():
        if module_stats['avg_score']:
            module_stats['avg_score'] = round(np.mean(module_stats['avg_score']), 4)
        else:
            module_stats['avg_score'] = 0.0
    
    return scored_questions, stats

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validation biomédicale via BioBERT")
    parser.add_argument('--in', dest='input_file', required=True, help='Fichier questions générées')
    parser.add_argument('--out', required=True, help='Fichier questions scorées de sortie')
    parser.add_argument('--metadata', required=True, help='Fichier metadata.json (seuils adaptatifs)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VALIDATION BIOMÉDICALE - BioBERT")
    print("="*60)
    
    # Charge metadata (seuils adaptatifs)
    print(f"\n📂 Chargement metadata : {args.metadata}")
    with open(args.metadata, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    thresholds = metadata.get('biomedical_thresholds', {})
    print(f"   ✓ Seuils adaptatifs chargés pour {len(thresholds)} modules")
    
    # Charge questions
    print(f"\n📂 Chargement questions : {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    print(f"   ✓ {len(questions)} questions chargées")
    
    # Initialise scorer BioBERT
    scorer = BioBERTScorer()
    
    # Scoring
    scored_questions, stats = score_questions(questions, scorer, thresholds)
    
    # Affichage résultats
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS VALIDATION BioBERT")
    print(f"{'='*60}")
    print(f"Questions scorées : {stats['scored']}")
    print(f"Questions validées : {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)")
    print(f"Questions rejetées : {stats['rejected']} ({stats['rejected']/stats['total']*100:.1f}%)")
    
    print(f"\n📊 Par module (top 10) :")
    sorted_modules = sorted(
        stats['by_module'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )[:10]
    
    for module_id, module_stats in sorted_modules:
        passed_pct = module_stats['passed'] / module_stats['total'] * 100
        threshold = thresholds.get(module_id, 0.05)
        print(f"  {module_id:20s} : {module_stats['passed']:3d}/{module_stats['total']:3d} passées ({passed_pct:5.1f}%) | score moy: {module_stats['avg_score']:.3f} | seuil: {threshold:.2f}")
    
    # Validation objectif global
    rejection_rate = stats['rejected'] / stats['total'] * 100
    
    if rejection_rate < 20:
        print(f"\n✅ OBJECTIF ATTEINT : taux rejet {rejection_rate:.1f}% < 20%")
    else:
        print(f"\n⚠️  OBJECTIF NON ATTEINT : taux rejet {rejection_rate:.1f}% ≥ 20%")
        print(f"   Suggestions:")
        print(f"   - Abaisser seuils pour modules à fort rejet")
        print(f"   - Améliorer prompts de génération")
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'validated_at': datetime.now().isoformat(),
        'stats': stats,
        'questions': scored_questions
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Questions scorées sauvegardées : {args.out}")
    
    print(f"\n{'='*60}")
    print(f"✅ VALIDATION BioBERT TERMINÉE")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    exit(main())

