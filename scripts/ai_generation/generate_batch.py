#!/usr/bin/env python3
"""
Script de génération batch de QCM via Ollama Mistral 7B
Tâches [020-022] - Phase 3 : Génération QCM

Objectif:
- Générer 2500+ QCM ancrés dans le texte du corpus
- Prompt engineering strict pour fidélité au texte
- Parsing JSON robuste avec retry logic
- Batch processing sur tous modules/chunks

Usage:
    python scripts/ai_generation/generate_batch.py \
           --modules src/data/modules/ \
           --keywords src/data/keywords.json \
           --profile src/data/annales_profile.json \
           --out src/data/questions/generated_raw.json \
           --model mistral:latest \
           --per-chunk 3
"""

import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from ollama import Client
    from tqdm import tqdm
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install ollama tqdm")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

MAX_RETRIES = 3
RETRY_DELAY = 2  # secondes
MAX_WORKERS = 4  # Parallélisation : 4 chunks simultanés
PROGRESS_FILE = "logs/generation_progress.json"  # Fichier de progression

# Lock pour accès thread-safe au fichier de progression
progress_lock = threading.Lock()

# =============================================================================
# PROMPTS
# =============================================================================

SYSTEM_PROMPT = """Tu es un expert IADE (Infirmier Anesthésiste Diplômé d'État). Génère des QCM *factuels* UNIQUEMENT à partir du CONTEXTE fourni.

Règles impératives :
- 4 options, 1 correcte (les 3 autres doivent être plausibles mais fausses)
- Reprends les termes exacts du cours (fidélité lexicale)
- Pas d'ambiguïté, pas d'improvisation, pas d'extrapolation
- Style conforme aux annales IADE (énoncé clair, concis, précis)
- Cite toujours le contexte source (extrait 1-2 phrases)

Format de retour (JSON array strict) :
[
  {
    "text": "Question claire et précise se terminant par un point d'interrogation ?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 0,
    "explanation": "Explication détaillée citant le cours. 3-5 lignes maximum.",
    "source_context": "Citation textuelle de 1-2 phrases du cours."
  }
]

IMPORTANT : Retourne UNIQUEMENT le JSON array, sans texte avant ou après."""

def build_user_prompt(module_id: str, section_title: str, chunk_text: str, 
                      keywords: List[str], annales_profile: Dict) -> str:
    """Construit le prompt utilisateur pour un chunk donné."""
    
    # Starters recommandés depuis profil annales
    starters = annales_profile.get('common_starters', ['Quelle est', 'Parmi les propositions'])
    starters_str = ', '.join(f'"{s}"' for s in starters[:3])
    
    avg_length = annales_profile.get('avg_question_length', 95)
    
    prompt = f"""[MODULE] : {module_id.replace('_', ' ').title()}
[SECTION] : {section_title}

[CONTEXTE SOURCE] :
{chunk_text}

[MOTS-CLÉS ATTENDUS] : {', '.join(keywords[:10]) if keywords else 'N/A'}

[CONSIGNES STYLE] :
- Longueur énoncé : environ {avg_length} caractères
- Débute par : {starters_str}
- Style : précis, factuel, examens IADE

Génère 2-3 QCM basés sur ce contexte."""
    
    return prompt

# =============================================================================
# GÉNÉRATION ET PARSING
# =============================================================================

def generate_qcm_for_chunk(
    client: Client,
    model: str,
    module_id: str,
    section_title: str,
    chunk: Dict,
    keywords: List[str],
    annales_profile: Dict
) -> List[Dict]:
    """
    Génère des QCM pour un chunk donné.
    
    Returns:
        Liste de QCM générés (peut être vide si échec)
    """
    chunk_text = chunk['text']
    chunk_id = chunk['chunk_id']
    
    # Construction du prompt
    user_prompt = build_user_prompt(
        module_id, section_title, chunk_text,
        keywords, annales_profile
    )
    
    # Tentatives avec retry
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_prompt}
                ],
                format='json',
                options={
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            )
            
            # Parse la réponse
            content = response['message']['content']
            
            # Nettoyage éventuel (si Mistral ajoute du texte avant/après)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            parsed = json.loads(content)
            
            # Gestion des différents formats de réponse Mistral
            if isinstance(parsed, dict):
                # Cas 1: {"QCM": [...]} ou {"questions": [...]}
                if 'QCM' in parsed:
                    qcm_list = parsed['QCM']
                elif 'questions' in parsed:
                    qcm_list = parsed['questions']
                else:
                    # Cas 2: un seul QCM en dict
                    qcm_list = [parsed]
            else:
                # Cas 3: array direct
                qcm_list = parsed
            
            # Assure que c'est une liste
            if not isinstance(qcm_list, list):
                qcm_list = [qcm_list]
            
            # Validation et enrichissement
            valid_qcms = []
            for qcm in qcm_list:
                # Validation format
                if not validate_qcm_format(qcm):
                    continue
                
                # Enrichissement avec métadonnées
                qcm['module_id'] = module_id
                qcm['chunk_id'] = chunk_id
                qcm['source_pdf'] = chunk['source_pdf']
                qcm['page'] = chunk.get('page_start', 0)
                
                valid_qcms.append(qcm)
            
            if valid_qcms:
                return valid_qcms
            else:
                # Retry si aucun QCM valide
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return []
            
        except json.JSONDecodeError as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return []
        
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return []
    
    return []

def validate_qcm_format(qcm: Dict) -> bool:
    """
    Valide le format d'un QCM généré.
    
    Returns:
        True si format valide, False sinon
    """
    required_keys = ['text', 'options', 'correctAnswer', 'explanation']
    
    # Check clés requises
    if not all(key in qcm for key in required_keys):
        return False
    
    # Check 4 options
    if not isinstance(qcm['options'], list) or len(qcm['options']) != 4:
        return False
    
    # Check options non vides et distinctes
    if any(not opt or not isinstance(opt, str) for opt in qcm['options']):
        return False
    
    if len(set(qcm['options'])) != 4:
        return False
    
    # Check correctAnswer
    if not isinstance(qcm['correctAnswer'], int) or qcm['correctAnswer'] not in [0, 1, 2, 3]:
        return False
    
    # Check texte non vide
    if not qcm['text'] or not qcm['explanation']:
        return False
    
    # Check source_context (peut être ajouté par le modèle ou après)
    if 'source_context' not in qcm:
        qcm['source_context'] = qcm['text'][:200]  # Fallback
    
    return True

# =============================================================================
# BATCH PROCESSING
# =============================================================================

def update_progress(total: int, completed: int, successful: int, failed: int, qcms_count: int):
    """Met à jour le fichier de progression (thread-safe)."""
    with progress_lock:
        progress = {
            'total_chunks': total,
            'completed_chunks': completed,
            'successful_chunks': successful,
            'failed_chunks': failed,
            'qcms_generated': qcms_count,
            'progress_percent': (completed / total * 100) if total > 0 else 0,
            'success_rate': (successful / completed * 100) if completed > 0 else 0,
            'last_update': datetime.now().isoformat()
        }
        
        try:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Ignore erreurs écriture

def generate_chunk_wrapper(args):
    """Wrapper pour parallélisation."""
    client, model, module_id, section_title, chunk, module_keywords, annales_profile = args
    
    # Skip chunks trop courts
    if len(chunk.get('text', '')) < 100:
        return None
    
    qcms = generate_qcm_for_chunk(
        client, model, module_id, section_title,
        chunk, module_keywords, annales_profile
    )
    
    return qcms if qcms else None

def generate_batch(
    modules_dir: Path,
    keywords_data: Dict,
    annales_profile: Dict,
    model: str,
    per_chunk: int
) -> List[Dict]:
    """
    Génère des QCM pour tous les modules et chunks (PARALLÉLISÉ).
    
    Returns:
        Liste de tous les QCM générés
    """
    all_qcms = []
    
    # Stats
    total_chunks = 0
    successful_chunks = 0
    failed_chunks = 0
    
    # Collecte tous les chunks à traiter
    tasks = []
    
    # Trouve tous les modules
    module_files = list(modules_dir.glob("*.json"))
    module_files = [f for f in module_files if f.stem not in ['reclassification_proposals']]
    
    print(f"\n📁 {len(module_files)} modules à traiter")
    print(f"🎯 Objectif : {per_chunk} QCM par chunk")
    print(f"⚡ Parallélisation : {MAX_WORKERS} workers")
    
    # Préparation tâches
    for module_file in sorted(module_files):
        module_id = module_file.stem
        
        with open(module_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)
        
        module_keywords = keywords_data.get(module_id, {}).get('module_keywords', [])
        
        for section in module_data.get('sections', []):
            section_title = section.get('title', 'Sans titre')
            
            for chunk in section.get('chunks', []):
                # Chaque client Ollama doit être créé dans son thread
                tasks.append((
                    None,  # Client sera créé dans le thread
                    model,
                    module_id,
                    section_title,
                    chunk,
                    module_keywords,
                    annales_profile
                ))
                total_chunks += 1
    
    print(f"\n📊 {total_chunks} chunks à traiter")
    
    # Initialise progression
    update_progress(total_chunks, 0, 0, 0, 0)
    
    # Exécution parallèle
    print(f"\n🚀 Démarrage génération parallèle ({MAX_WORKERS} workers)...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Crée les clients dans chaque thread
        def task_with_client(args):
            task_args = list(args)
            task_args[0] = Client()  # Client local au thread
            return generate_chunk_wrapper(tuple(task_args))
        
        # Soumet toutes les tâches
        futures = {executor.submit(task_with_client, task): task for task in tasks}
        
        # Progress bar
        completed = 0
        with tqdm(total=total_chunks, desc="Génération globale", unit="chunk") as pbar:
            for future in as_completed(futures):
                completed += 1
                
                try:
                    result = future.result()
                    
                    if result:
                        all_qcms.extend(result)
                        successful_chunks += 1
                    else:
                        failed_chunks += 1
                    
                    # Met à jour progression toutes les 5 chunks
                    if completed % 5 == 0 or completed == total_chunks:
                        update_progress(total_chunks, completed, successful_chunks, failed_chunks, len(all_qcms))
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        'QCM': len(all_qcms),
                        'Réussite': f"{(successful_chunks/completed*100):.1f}%"
                    })
                    
                except Exception as e:
                    failed_chunks += 1
                    pbar.update(1)
    
    # Stats finales
    success_rate = (successful_chunks / total_chunks * 100) if total_chunks > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 STATISTIQUES GÉNÉRATION")
    print(f"{'='*60}")
    print(f"Chunks traités : {total_chunks}")
    print(f"Chunks réussis : {successful_chunks}")
    print(f"Chunks échoués : {failed_chunks}")
    print(f"Taux succès : {success_rate:.1f}%")
    print(f"QCM générés : {len(all_qcms)}")
    
    # Update finale
    update_progress(total_chunks, total_chunks, successful_chunks, failed_chunks, len(all_qcms))
    
    return all_qcms

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Génération batch de QCM via Ollama Mistral")
    parser.add_argument('--modules', required=True, help='Dossier modules JSON')
    parser.add_argument('--keywords', required=True, help='Fichier keywords.json')
    parser.add_argument('--profile', required=True, help='Fichier annales_profile.json')
    parser.add_argument('--out', required=True, help='Fichier generated_raw.json de sortie')
    parser.add_argument('--model', default='mistral:latest', help='Modèle Ollama (défaut: mistral:latest)')
    parser.add_argument('--per-chunk', type=int, default=3, help='Nombre QCM par chunk (défaut: 3)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("GÉNÉRATION BATCH QCM - OLLAMA MISTRAL 7B")
    print("="*60)
    
    # Charge keywords
    print(f"\n📂 Chargement keywords : {args.keywords}")
    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords_data = json.load(f)
    print(f"   ✓ {len(keywords_data)} modules indexés")
    
    # Charge profil annales
    print(f"\n📂 Chargement profil annales : {args.profile}")
    with open(args.profile, 'r', encoding='utf-8') as f:
        annales_profile = json.load(f)
    print(f"   ✓ Profil chargé")
    
    # Test connexion Ollama
    print(f"\n🔧 Test connexion Ollama...")
    try:
        client = Client()
        print(f"   ✓ Connexion OK")
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        print(f"   Vérifiez que Ollama est démarré (ollama serve)")
        return 1
    
    # Génération batch
    print(f"\n🚀 Démarrage génération batch...")
    print(f"   Modèle : {args.model}")
    print(f"   QCM par chunk : {args.per_chunk}")
    
    start_time = time.time()
    
    qcms = generate_batch(
        Path(args.modules),
        keywords_data,
        annales_profile,
        args.model,
        args.per_chunk
    )
    
    elapsed_time = time.time() - start_time
    
    # Vérification objectif
    print(f"\n{'='*60}")
    if len(qcms) >= 2500:
        print(f"✅ OBJECTIF ATTEINT : {len(qcms)} QCM générés (≥ 2500)")
    elif len(qcms) >= 2000:
        print(f"⚠️  OBJECTIF PROCHE : {len(qcms)} QCM générés (objectif: ≥ 2500)")
    else:
        print(f"❌ OBJECTIF NON ATTEINT : {len(qcms)} QCM générés (objectif: ≥ 2500)")
        print(f"   Suggestion: augmenter --per-chunk ou améliorer taux succès")
    print(f"{'='*60}")
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'model': args.model,
        'total_qcms': len(qcms),
        'generation_time_seconds': round(elapsed_time, 2),
        'questions': qcms
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 QCM sauvegardés : {args.out}")
    print(f"⏱️  Temps total : {elapsed_time/60:.1f} minutes")
    
    print("\n" + "="*60)
    print("✅ GÉNÉRATION BATCH TERMINÉE")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())

