#!/usr/bin/env python3
"""
Script de génération du rapport de couverture
Tâche [065] - Phase 5 : Compilation & Examens

Objectif:
- Synthèse: nb QCM/module, couverture pages, taux rejet
- Moyennes scores (BioBERT, context, keywords)
- Liste chunks orphelins

Usage:
    python scripts/reports/coverage_report.py \
           --modules src/data/modules/ \
           --questions validated.json \
           --out docs/coverage_report.md
"""

import argparse
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Génération rapport de couverture")
    parser.add_argument('--modules', required=True, help='Dossier modules')
    parser.add_argument('--questions', required=True, help='Fichier validated.json')
    parser.add_argument('--out', required=True, help='Fichier coverage_report.md')
    
    args = parser.parse_args()
    
    # Charge modules
    modules_dir = Path(args.modules)
    all_chunks = {}
    
    for module_file in modules_dir.glob("*.json"):
        if module_file.stem == 'reclassification_proposals':
            continue
        
        with open(module_file, 'r', encoding='utf-8') as f:
            module_data = json.load(f)
        
        module_id = module_file.stem
        all_chunks[module_id] = set()
        
        for section in module_data.get('sections', []):
            for chunk in section.get('chunks', []):
                all_chunks[module_id].add(chunk['chunk_id'])
    
    # Charge questions
    with open(args.questions, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', []) if isinstance(data, dict) else data
    
    # Analyse par module
    by_module = {}
    chunks_covered = set()
    
    for question in questions:
        module_id = question.get('module_id', 'unknown')
        chunk_id = question.get('chunk_id', '')
        
        if module_id not in by_module:
            by_module[module_id] = {
                'questions_count': 0,
                'avg_biomedical': [],
                'avg_context': [],
                'avg_keywords': []
            }
        
        by_module[module_id]['questions_count'] += 1
        by_module[module_id]['avg_biomedical'].append(question.get('biomedical_score', 0))
        by_module[module_id]['avg_context'].append(question.get('context_score', 0))
        by_module[module_id]['avg_keywords'].append(question.get('keywords_overlap', 0))
        
        if chunk_id:
            chunks_covered.add(chunk_id)
    
    # Calcul moyennes
    for module_stats in by_module.values():
        if module_stats['avg_biomedical']:
            module_stats['avg_biomedical'] = sum(module_stats['avg_biomedical']) / len(module_stats['avg_biomedical'])
        else:
            module_stats['avg_biomedical'] = 0
        
        if module_stats['avg_context']:
            module_stats['avg_context'] = sum(module_stats['avg_context']) / len(module_stats['avg_context'])
        else:
            module_stats['avg_context'] = 0
        
        if module_stats['avg_keywords']:
            module_stats['avg_keywords'] = sum(module_stats['avg_keywords']) / len(module_stats['avg_keywords'])
        else:
            module_stats['avg_keywords'] = 0
    
    # Génération rapport Markdown
    report_lines = [
        "# Rapport de Couverture - IADE NEW",
        "",
        f"**Date**: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "## Vue d'ensemble",
        "",
        f"- **Questions totales**: {len(questions)}",
        f"- **Modules couverts**: {len(by_module)}",
        f"- **Chunks couverts**: {len(chunks_covered)}",
        "",
        "## Par Module",
        "",
        "| Module | Questions | Avg BioBERT | Avg Context | Avg Keywords |",
        "|--------|-----------|-------------|-------------|--------------|"
    ]
    
    for module_id in sorted(by_module.keys()):
        stats = by_module[module_id]
        report_lines.append(
            f"| {module_id:20s} | {stats['questions_count']:4d} | "
            f"{stats['avg_biomedical']:.3f} | {stats['avg_context']:.3f} | {stats['avg_keywords']:.3f} |"
        )
    
    report_lines.extend([
        "",
        f"## Couverture Corpus",
        "",
        f"Chunks totaux disponibles: {sum(len(chunks) for chunks in all_chunks.values())}",
        f"Chunks avec QCM: {len(chunks_covered)}",
        f"Couverture: {len(chunks_covered) / sum(len(chunks) for chunks in all_chunks.values()) * 100:.1f}%",
        "",
        "---",
        f"*Généré automatiquement le {datetime.now().isoformat()}*"
    ])
    
    # Sauvegarde
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✅ Rapport sauvegardé : {args.out}")
    
    return 0

if __name__ == "__main__":
    exit(main())

