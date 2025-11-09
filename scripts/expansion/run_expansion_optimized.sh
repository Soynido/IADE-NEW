#!/bin/bash

# Pipeline d'expansion OPTIMISÉE - Phase 12
# Résout les problèmes de timeout et améliore le taux de réussite

set -e  # Arrêt si erreur

cd "$(dirname "$0")/../.."

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     🚀 PIPELINE EXPANSION OPTIMISÉE - Phase 12          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Vérifier environnement Python
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    exit 1
fi

source venv/bin/activate

echo "✅ Environnement activé"
echo ""

# ÉTAPE 1: Extraction (skip si déjà fait)
if [ ! -f "src/data/raw/pages_metadata.json" ]; then
    echo "============================================================"
    echo "📚 ÉTAPE 1/4 : Extraction pages..."
    echo "============================================================"
    python scripts/expansion/extract_pages.py
    echo ""
else
    echo "✅ Étape 1 : Extraction déjà effectuée"
    echo ""
fi

# ÉTAPE 2: Génération OPTIMISÉE
echo "============================================================"
echo "⚡ ÉTAPE 2/4 : Génération QCM OPTIMISÉE..."
echo "============================================================"
python scripts/expansion/generate_massive_optimized.py
echo ""

# ÉTAPE 3: Validation BioBERT
echo "============================================================"
echo "🔬 ÉTAPE 3/4 : Validation BioBERT..."
echo "============================================================"
python scripts/expansion/validate_massive.py
echo ""

# ÉTAPE 4: Fusion avec corpus existant
echo "============================================================"
echo "🔀 ÉTAPE 4/4 : Fusion avec corpus existant..."
echo "============================================================"
python scripts/expansion/merge_with_existing.py
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     ✅ PIPELINE EXPANSION OPTIMISÉE TERMINÉ             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if [ -f "src/data/questions/expansion_summary.txt" ]; then
    cat src/data/questions/expansion_summary.txt
fi

