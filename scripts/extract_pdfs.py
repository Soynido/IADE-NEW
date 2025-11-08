#!/usr/bin/env python3
"""
Script d'extraction et segmentation des PDF sources
Tâche [010-011] - Phase 1 : Extraction PDF

Objectif:
- Extraire le contenu des 3 PDF sources
- Détecter les titres de chapitres/sections (heuristiques + regex)
- Découper en chunks < 1200 tokens
- Générer modules/*.json avec structure hiérarchique

Usage:
    python scripts/extract_pdfs.py --input "src/data/sources/*.pdf" \
                                   --out src/data/modules/ \
                                   --metadata src/data/metadata.json
"""

import argparse
import json
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install PyPDF2 pdfplumber")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Patterns regex pour détection de titres
TITLE_PATTERNS = [
    r'^\s*CHAPITRE\s+[IVXLCDM0-9]+\s*[:\-–—]?\s*.+$',  # CHAPITRE I : Titre
    r'^\s*PARTIE\s+[IVXLCDM0-9]+\s*[:\-–—]?\s*.+$',    # PARTIE I : Titre
    r'^\s*\d+\.?\s+[A-ZÀÂÇÉÈÊËÏÎÔÛÙÜŸÆŒ]{3,}.+$',      # 1. TITRE MAJUSCULES
    r'^\s*[IVXLCDM]+\.\s+[A-ZÀÂÇÉÈÊËÏÎÔÛÙÜŸÆŒ]{3,}.+$',  # I. TITRE MAJUSCULES
    r'^\s*[A-ZÀÂÇÉÈÊËÏÎÔÛÙÜŸÆŒ\s]{10,}$',              # TITRE TOUT MAJUSCULES (min 10 char)
]

# Mots-clés seed par module (pour classification automatique)
MODULE_KEYWORDS = {
    "bases_physio": ["cellule", "homéostasie", "compartiment", "osmolarité", "pH", "électrolyte"],
    "respiratoire": ["PEEP", "ventilation", "PaO2", "FiO2", "capnographie", "compliance", "oxygénation"],
    "cardio": ["PVC", "PAM", "débit cardiaque", "hémodynamique", "précharge", "amines", "choc"],
    "neuro": ["PIC", "PPC", "GCS", "sédation", "cérébral", "neurologie", "conscience"],
    "pharma_generaux": ["propofol", "étomidate", "kétamine", "thiopental", "anesthésie générale"],
    "pharma_locaux": ["lidocaïne", "bupivacaïne", "ropivacaïne", "anesthésie locale", "ALR"],
    "pharma_opioides": ["morphine", "fentanyl", "sufentanil", "opioïde", "palier", "analgésie"],
    "pharma_curares": ["rocuronium", "atracurium", "sugammadex", "curare", "myorelaxant"],
    "alr": ["rachianesthésie", "péridurale", "bloc", "locorégionale"],
    "ventilation": ["intubation", "LMA", "VNI", "VMI", "EtCO2", "voies aériennes"],
    "transfusion": ["CGR", "PFC", "plaquettes", "ROTEM", "TEG", "hémostase", "transfusion"],
    "reanimation": ["sepsis", "SDRA", "réanimation", "choc", "polytrauma", "brûlé"],
    "douleur": ["douleur", "échelle", "PCA", "EVA", "analgésie", "co-antalgique"],
    "infectio": ["antibiotique", "infection", "asepsie", "SSI", "ISO", "hygiène"],
    "monitorage": ["SpO2", "EtCO2", "NIBP", "IBP", "BIS", "monitorage", "surveillance"],
    "pediatrie": ["pédiatrie", "enfant", "gériatrie", "grossesse", "obésité"],
    "legislation": ["consentement", "législation", "éthique", "traçabilité", "vigilance"]
}

MAX_CHUNK_TOKENS = 1200  # Limite pour Mistral 7B

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def estimate_tokens(text: str) -> int:
    """Estime le nombre de tokens (approximation : 1 token ≈ 4 caractères)."""
    return len(text) // 4

def normalize_text(text: str) -> str:
    """
    Normalise le texte extrait :
    - Supprime en-têtes/pieds de page répétitifs
    - Supprime numéros de page isolés
    - Normalise les espaces
    """
    # Supprime numéros de page isolés
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Supprime lignes très courtes répétitives (en-têtes/pieds)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Garde les lignes vides ou suffisamment longues
        if not stripped or len(stripped) > 15:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Normalise les espaces multiples
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def is_title(line: str) -> bool:
    """
    Détermine si une ligne est un titre de chapitre/section.
    Utilise des patterns regex et heuristiques.
    """
    line = line.strip()
    
    # Vide ou trop court
    if not line or len(line) < 5:
        return False
    
    # Check regex patterns
    for pattern in TITLE_PATTERNS:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    
    # Heuristiques additionnelles
    # 1. Ligne courte (< 100 char) et majoritairement en majuscules
    if len(line) < 100:
        uppercase_ratio = sum(1 for c in line if c.isupper()) / len(line)
        if uppercase_ratio > 0.6:
            return True
    
    # 2. Commence par un numéro suivi de mots capitalisés
    if re.match(r'^\d+\.?\s+[A-ZÀÂÇÉÈÊËÏÎÔÛÙÜŸ]', line):
        return True
    
    return False

def classify_module(text: str, keywords_density: Dict[str, float] = None) -> str:
    """
    Classifie un texte dans un module thématique basé sur les mots-clés.
    Retourne l'ID du module le plus probable.
    """
    text_lower = text.lower()
    scores = {}
    
    for module_id, keywords in MODULE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Count occurrences (pondéré par longueur du keyword)
            count = text_lower.count(keyword.lower())
            score += count * len(keyword)
        scores[module_id] = score
    
    # Retourne le module avec le score le plus élevé (ou "unknown" si aucun)
    if max(scores.values()) == 0:
        return "unknown"
    
    return max(scores, key=scores.get)

def split_into_chunks(text: str, max_tokens: int = MAX_CHUNK_TOKENS) -> List[str]:
    """
    Découpe un texte en chunks de max_tokens tokens maximum.
    Essaie de couper aux limites de paragraphes.
    """
    chunks = []
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        # Si le paragraphe seul dépasse la limite, on le coupe
        if para_tokens > max_tokens:
            # Sauve le chunk en cours
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_tokens = 0
            
            # Coupe le paragraphe en phrases
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                
                if current_tokens + sent_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                    current_tokens = sent_tokens
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
                    current_tokens += sent_tokens
        
        # Si ajouter ce paragraphe dépasse la limite
        elif current_tokens + para_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
            current_tokens = para_tokens
        
        # Sinon, on ajoute le paragraphe au chunk courant
        else:
            current_chunk += "\n\n" + para if current_chunk else para
            current_tokens += para_tokens
    
    # Ajoute le dernier chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# =============================================================================
# EXTRACTION PDF
# =============================================================================

def extract_pdf_content(pdf_path: str) -> List[Dict]:
    """
    Extrait le contenu d'un PDF avec détection de titres et découpage en chunks.
    
    Returns:
        List de dicts avec structure:
        {
            'page': int,
            'type': 'title' | 'content',
            'text': str,
            'level': int (pour les titres)
        }
    """
    print(f"\n📄 Extraction de : {Path(pdf_path).name}")
    
    elements = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"   {total_pages} pages détectées")
            
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                
                if not text:
                    continue
                
                # Normalisation
                text = normalize_text(text)
                
                # Découpe en lignes pour détection de titres
                lines = text.split('\n')
                current_content = []
                
                for line in lines:
                    if is_title(line):
                        # Sauve le contenu accumulé
                        if current_content:
                            content_text = '\n'.join(current_content)
                            elements.append({
                                'page': page_num,
                                'type': 'content',
                                'text': content_text
                            })
                            current_content = []
                        
                        # Ajoute le titre
                        elements.append({
                            'page': page_num,
                            'type': 'title',
                            'text': line.strip(),
                            'level': 1  # Simplifié (tous niveau 1)
                        })
                    else:
                        current_content.append(line)
                
                # Sauve le contenu restant de la page
                if current_content:
                    content_text = '\n'.join(current_content)
                    elements.append({
                        'page': page_num,
                        'type': 'content',
                        'text': content_text
                    })
            
            print(f"   ✓ {len(elements)} éléments extraits")
            return elements
            
    except Exception as e:
        print(f"   ❌ Erreur d'extraction: {e}")
        return []

def structure_into_sections(elements: List[Dict], pdf_filename: str) -> List[Dict]:
    """
    Structure les éléments extraits en sections hiérarchiques.
    Chaque section contient un titre et son contenu découpé en chunks.
    """
    sections = []
    current_section = None
    
    for elem in elements:
        if elem['type'] == 'title':
            # Sauve la section précédente
            if current_section and current_section['content']:
                sections.append(current_section)
            
            # Nouvelle section
            current_section = {
                'title': elem['text'],
                'page_start': elem['page'],
                'page_end': elem['page'],
                'content': []
            }
        
        elif elem['type'] == 'content' and current_section:
            current_section['content'].append(elem['text'])
            current_section['page_end'] = elem['page']
    
    # Sauve la dernière section
    if current_section and current_section['content']:
        sections.append(current_section)
    
    # Découpe le contenu de chaque section en chunks
    structured_sections = []
    for idx, section in enumerate(sections, start=1):
        full_content = '\n\n'.join(section['content'])
        chunks = split_into_chunks(full_content)
        
        # Classifie le module basé sur le contenu total
        module_id = classify_module(full_content)
        
        section_id = f"section_{idx:02d}"
        
        structured_section = {
            'section_id': section_id,
            'title': section['title'],
            'pages': list(range(section['page_start'], section['page_end'] + 1)),
            'module_id': module_id,
            'chunks': [
                {
                    'chunk_id': f"{section_id}_c{i:02d}",
                    'text': chunk,
                    'source_pdf': pdf_filename,
                    'page_start': section['page_start'],
                    'page_end': section['page_end'],
                    'token_count': estimate_tokens(chunk)
                }
                for i, chunk in enumerate(chunks, start=1)
            ]
        }
        
        structured_sections.append(structured_section)
    
    return structured_sections

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Extraction et segmentation des PDF sources")
    parser.add_argument('--input', required=True, help='Pattern glob des PDF sources')
    parser.add_argument('--out', required=True, help='Dossier de sortie pour les modules')
    parser.add_argument('--metadata', required=True, help='Fichier metadata.json à générer')
    
    args = parser.parse_args()
    
    print("="*60)
    print("EXTRACTION PDF → MODULES")
    print("="*60)
    
    # Trouve les fichiers PDF
    pdf_files = glob.glob(args.input)
    if not pdf_files:
        print(f"❌ Aucun fichier trouvé pour le pattern: {args.input}")
        return 1
    
    print(f"\n📁 {len(pdf_files)} fichiers PDF trouvés")
    
    # Créer le dossier de sortie
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Extraction de tous les PDF
    all_sections = []
    sources_info = []
    
    for pdf_path in pdf_files:
        elements = extract_pdf_content(pdf_path)
        
        if not elements:
            continue
        
        pdf_filename = Path(pdf_path).name
        sections = structure_into_sections(elements, pdf_filename)
        all_sections.extend(sections)
        
        # Info pour metadata
        sources_info.append({
            'file': pdf_filename,
            'type': 'cours' if 'Prepaconcoursiade' in pdf_filename else 'annales',
            'sections_count': len(sections)
        })
    
    print(f"\n✓ {len(all_sections)} sections extraites au total")
    
    # Groupe par module
    modules = {}
    for section in all_sections:
        module_id = section['module_id']
        if module_id not in modules:
            modules[module_id] = {
                'module_id': module_id,
                'title': f"Module {module_id.replace('_', ' ').title()}",
                'sections': []
            }
        modules[module_id]['sections'].append(section)
    
    # Sauvegarde chaque module dans un fichier JSON
    print(f"\n💾 Sauvegarde de {len(modules)} modules...")
    for module_id, module_data in modules.items():
        module_file = out_dir / f"{module_id}.json"
        with open(module_file, 'w', encoding='utf-8') as f:
            json.dump(module_data, f, ensure_ascii=False, indent=2)
        
        total_chunks = sum(len(s['chunks']) for s in module_data['sections'])
        print(f"   ✓ {module_id}.json : {len(module_data['sections'])} sections, {total_chunks} chunks")
    
    # Génère metadata.json
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'sources': sources_info,
        'modules': {
            module_id: {
                'title': data['title'],
                'sections_count': len(data['sections']),
                'chunks_count': sum(len(s['chunks']) for s in data['sections'])
            }
            for module_id, data in modules.items()
        },
        'total_sections': len(all_sections),
        'total_chunks': sum(sum(len(s['chunks']) for s in data['sections']) for data in modules.values())
    }
    
    metadata_path = Path(args.metadata)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Metadata sauvegardé : {args.metadata}")
    
    print("\n" + "="*60)
    print("✅ EXTRACTION TERMINÉE")
    print("="*60)
    print(f"Modules générés : {len(modules)}")
    print(f"Sections totales : {len(all_sections)}")
    print(f"Chunks totaux : {metadata['total_chunks']}")
    
    return 0

if __name__ == "__main__":
    exit(main())

