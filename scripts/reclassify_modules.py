#!/usr/bin/env python3
"""
Script de re-classification des modules "unknown"
Tâche [014] - Phase 1 : Validation manuelle taxonomie

Analyse les sections "unknown" et propose des re-classifications
basées sur une analyse plus fine du contenu.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple
from datetime import datetime

# Mots-clés étendus pour meilleure classification
EXTENDED_KEYWORDS = {
    "bases_physio": {
        "keywords": ["cellule", "membrane", "homéostasie", "compartiment", "osmose", "osmolarité", 
                     "pH", "acide", "base", "électrolyte", "sodium", "potassium", "calcium",
                     "métabolisme", "ATP", "glycolyse", "mitochondrie"],
        "weight": 1.0
    },
    "respiratoire": {
        "keywords": ["PEEP", "ventilation", "PaO2", "PaCO2", "FiO2", "saturation", "oxygène",
                     "capnographie", "EtCO2", "CO2", "compliance", "résistance", "poumon",
                     "alvéole", "bronche", "trachée", "gaz", "hypoxie", "hypercapnie"],
        "weight": 1.0
    },
    "cardio": {
        "keywords": ["cœur", "cardiaque", "circulation", "PVC", "PAM", "pression", "artérielle",
                     "débit", "hémodynamique", "précharge", "postcharge", "contractilité",
                     "amine", "noradrénaline", "dobutamine", "remplissage", "choc",
                     "coronaire", "infarctus", "insuffisance", "vascularisation", "innervation"],
        "weight": 1.2
    },
    "neuro": {
        "keywords": ["PIC", "PPC", "GCS", "Glasgow", "sédation", "cérébral", "neurologie",
                     "conscience", "pupille", "neuroprotection", "perfusion", "cerveau",
                     "méningé", "AVC", "trauma", "crânien"],
        "weight": 1.0
    },
    "pharma_generaux": {
        "keywords": ["propofol", "étomidate", "kétamine", "thiopental", "anesthésie", "générale",
                     "agent", "intraveineux", "induction", "entretien", "réveil"],
        "weight": 1.5
    },
    "pharma_locaux": {
        "keywords": ["lidocaïne", "bupivacaïne", "ropivacaïne", "mépivacaïne", "local",
                     "anesthésique", "bloc", "infiltration", "toxicité"],
        "weight": 1.5
    },
    "pharma_opioides": {
        "keywords": ["morphine", "fentanyl", "sufentanil", "rémifentanil", "opioïde", "opiacé",
                     "palier", "OMS", "analgésie", "analgésique", "douleur", "naloxone"],
        "weight": 1.5
    },
    "pharma_curares": {
        "keywords": ["rocuronium", "atracurium", "cisatracurium", "vécuronium", "succinylcholine",
                     "curare", "myorelaxant", "sugammadex", "décurarisation", "bloc", "neuromusculaire"],
        "weight": 1.5
    },
    "alr": {
        "keywords": ["rachianesthésie", "péridurale", "épidurale", "bloc", "locorégionale",
                     "périphérique", "plexus", "fémoral", "sciatique", "ponction"],
        "weight": 1.0
    },
    "ventilation": {
        "keywords": ["intubation", "tube", "LMA", "masque laryngé", "VNI", "VMI",
                     "voies aériennes", "trachéale", "larynx", "cricothyroïdotomie"],
        "weight": 1.0
    },
    "transfusion": {
        "keywords": ["CGR", "PFC", "plasma", "plaquettes", "culot", "globulaire", "transfusion",
                     "ROTEM", "TEG", "fibrinogène", "hémostase", "coagulation", "TS", "TP", "TCA"],
        "weight": 1.2
    },
    "reanimation": {
        "keywords": ["sepsis", "septique", "SDRA", "réanimation", "soins intensifs",
                     "défaillance", "organe", "polytrauma", "brûlé", "SRIS"],
        "weight": 1.0
    },
    "douleur": {
        "keywords": ["douleur", "EVA", "EN", "échelle", "PCA", "analgésie", "co-antalgique",
                     "paracétamol", "AINS", "anti-inflammatoire", "chronique"],
        "weight": 1.0
    },
    "infectio": {
        "keywords": ["antibioprophylaxie", "antibiotique", "infection", "asepsie", "antisepsie",
                     "SSI", "ISO", "hygiène", "décontamination", "stérile", "bactérie"],
        "weight": 1.0
    },
    "monitorage": {
        "keywords": ["SpO2", "saturomètre", "pulsioxymètre", "NIBP", "IBP", "BIS", "entropie",
                     "monitorage", "surveillance", "scope", "ECG", "capnographe"],
        "weight": 1.0
    },
    "pediatrie": {
        "keywords": ["pédiatrie", "enfant", "nouveau-né", "nourrisson", "gériatrie",
                     "personne âgée", "grossesse", "obstétrique", "obésité", "IMC"],
        "weight": 1.0
    },
    "legislation": {
        "keywords": ["consentement", "législation", "loi", "décret", "éthique", "déontologie",
                     "traçabilité", "vigilance", "responsabilité", "dossier", "patient"],
        "weight": 1.0
    }
}

def analyze_section(section: Dict) -> Tuple[str, float, List[str]]:
    """
    Analyse une section et propose une classification.
    
    Returns:
        (module_id, confidence_score, matched_keywords)
    """
    # Combine title + premier chunk pour analyse
    text = section['title'] + "\n"
    if section['chunks']:
        text += section['chunks'][0]['text']
    
    text_lower = text.lower()
    
    best_module = "unknown"
    best_score = 0
    best_keywords = []
    
    for module_id, config in EXTENDED_KEYWORDS.items():
        keywords = config['keywords']
        weight = config['weight']
        score = 0
        matched = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            if count > 0:
                score += count * len(keyword) * weight
                matched.append(keyword)
        
        if score > best_score:
            best_score = score
            best_module = module_id
            best_keywords = matched
    
    # Confidence : normalize par longueur du texte
    confidence = min(best_score / (len(text) / 100), 1.0) if text else 0.0
    
    return best_module, confidence, best_keywords

def reclassify_unknown_module(unknown_json_path: str, output_dir: Path):
    """
    Re-classifie les sections du module 'unknown'.
    """
    print("\n🔍 Analyse du module 'unknown'...")
    
    with open(unknown_json_path, 'r', encoding='utf-8') as f:
        unknown_data = json.load(f)
    
    sections = unknown_data['sections']
    print(f"   {len(sections)} sections à analyser")
    
    # Analyse chaque section
    reclassifications = Counter()
    high_confidence_moves = []
    low_confidence = []
    
    for section in sections:
        module_id, confidence, keywords = analyze_section(section)
        
        reclassifications[module_id] += 1
        
        if confidence > 0.3:
            high_confidence_moves.append({
                'section': section,
                'new_module': module_id,
                'confidence': confidence,
                'keywords': keywords
            })
        else:
            low_confidence.append({
                'section': section,
                'title': section['title'][:80],
                'confidence': confidence
            })
    
    # Affichage des résultats
    print(f"\n📊 Propositions de re-classification (confiance > 30%) :")
    for module_id, count in reclassifications.most_common():
        if module_id != "unknown":
            print(f"   → {module_id}: {count} sections")
    
    print(f"\n⚠️  Sections à faible confiance (< 30%) : {len(low_confidence)}")
    if low_confidence[:5]:
        print("   Exemples :")
        for item in low_confidence[:5]:
            print(f"     - \"{item['title']}\" (conf: {item['confidence']:.2f})")
    
    # Sauvegarde les propositions
    proposals_path = output_dir / "reclassification_proposals.json"
    with open(proposals_path, 'w', encoding='utf-8') as f:
        json.dump({
            'high_confidence': high_confidence_moves,
            'low_confidence': low_confidence,
            'summary': dict(reclassifications)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Propositions sauvegardées : {proposals_path}")
    
    return high_confidence_moves

def apply_reclassifications(modules_dir: Path, proposals: List[Dict]):
    """
    Applique les re-classifications proposées.
    """
    print(f"\n✏️  Application de {len(proposals)} re-classifications...")
    
    # Charge tous les modules existants
    modules = {}
    for module_file in modules_dir.glob("*.json"):
        module_id = module_file.stem
        with open(module_file, 'r', encoding='utf-8') as f:
            modules[module_id] = json.load(f)
    
    # Groupe propositions par module cible
    by_target = {}
    for prop in proposals:
        target = prop['new_module']
        if target not in by_target:
            by_target[target] = []
        by_target[target].append(prop['section'])
    
    # Ajoute sections aux modules cibles
    for target_module, sections in by_target.items():
        if target_module not in modules:
            # Crée nouveau module
            modules[target_module] = {
                'module_id': target_module,
                'title': f"Module {target_module.replace('_', ' ').title()}",
                'sections': []
            }
        
        # Ajoute sections + met à jour module_id dans chunks
        for section in sections:
            section['module_id'] = target_module
            for chunk in section['chunks']:
                # Met à jour chunk_id pour refléter le nouveau module
                old_chunk_id = chunk['chunk_id']
                new_chunk_id = f"{target_module}_{old_chunk_id}"
                chunk['chunk_id'] = new_chunk_id
            
            modules[target_module]['sections'].append(section)
        
        print(f"   ✓ {target_module}: +{len(sections)} sections")
    
    # Supprime les sections re-classifiées de "unknown"
    if 'unknown' in modules:
        remaining_sections = []
        moved_section_ids = {s['section_id'] for prop in proposals for s in [prop['section']]}
        
        for section in modules['unknown']['sections']:
            if section['section_id'] not in moved_section_ids:
                remaining_sections.append(section)
        
        modules['unknown']['sections'] = remaining_sections
        print(f"   ✓ unknown: {len(remaining_sections)} sections restantes")
    
    # Sauvegarde tous les modules
    for module_id, module_data in modules.items():
        if 'sections' not in module_data or not module_data['sections']:  # Skip modules vides
            continue
        
        module_file = modules_dir / f"{module_id}.json"
        with open(module_file, 'w', encoding='utf-8') as f:
            json.dump(module_data, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Re-classification appliquée")

def update_metadata(metadata_path: str, modules_dir: Path):
    """
    Met à jour metadata.json après re-classification.
    """
    print(f"\n🔄 Mise à jour de metadata.json...")
    
    # Recalcule les stats
    modules_info = {}
    total_chunks = 0
    total_sections = 0
    
    for module_file in sorted(modules_dir.glob("*.json")):
        module_id = module_file.stem
        
        # Skip fichiers non-module
        if module_id == 'reclassification_proposals':
            continue
        
        with open(module_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'sections' not in data:
            continue
        
        sections_count = len(data['sections'])
        chunks_count = sum(len(s['chunks']) for s in data['sections'])
        
        if sections_count > 0:  # Ignore modules vides
            modules_info[module_id] = {
                'title': data.get('title', f"Module {module_id}"),
                'sections_count': sections_count,
                'chunks_count': chunks_count
            }
            total_sections += sections_count
            total_chunks += chunks_count
    
    # Charge metadata existant
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Met à jour
    metadata['modules'] = modules_info
    metadata['total_sections'] = total_sections
    metadata['total_chunks'] = total_chunks
    metadata['reclassified_at'] = datetime.now().isoformat()
    
    # Sauvegarde
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Metadata mis à jour")
    print(f"  - Modules actifs : {len(modules_info)}")
    print(f"  - Sections totales : {total_sections}")
    print(f"  - Chunks totaux : {total_chunks}")

def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Re-classification modules unknown")
    parser.add_argument('--modules-dir', required=True, help='Dossier contenant les modules JSON')
    parser.add_argument('--metadata', required=True, help='Fichier metadata.json')
    parser.add_argument('--apply', action='store_true', help='Appliquer les re-classifications (sinon mode analyse uniquement)')
    
    args = parser.parse_args()
    
    modules_dir = Path(args.modules_dir)
    unknown_path = modules_dir / "unknown.json"
    
    if not unknown_path.exists():
        print("✓ Pas de module 'unknown' trouvé (déjà classifié)")
        return 0
    
    print("="*60)
    print("RE-CLASSIFICATION MODULE 'UNKNOWN'")
    print("="*60)
    
    # Analyse et propose re-classifications
    proposals = reclassify_unknown_module(str(unknown_path), modules_dir)
    
    if not args.apply:
        print("\n💡 Mode ANALYSE uniquement")
        print("   Utilisez --apply pour appliquer les re-classifications")
        return 0
    
    # Application
    if proposals:
        apply_reclassifications(modules_dir, proposals)
        update_metadata(args.metadata, modules_dir)
    else:
        print("\n⚠️  Aucune re-classification à appliquer")
    
    print("\n" + "="*60)
    print("✅ TERMINÉ")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())

