#!/bin/bash

# Pipeline complet d'expansion - Phase 12
# Multiplie le corpus par ~10

set -e  # Arrête si erreur

cd "$(dirname "$0")/../.."

echo "═══════════════════════════════════════════════════════════"
echo "🚀 PIPELINE D'EXPANSION MASSIVE - Phase 12"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Activate venv
source venv/bin/activate

# Étape 1: Extraction page par page
echo "📚 ÉTAPE 1/4 : Extraction pages..."
python scripts/expansion/extract_pages.py
echo ""

# Étape 2: Génération massive (3 QCM/page)
echo "⚡ ÉTAPE 2/4 : Génération QCM (peut prendre 1-2h)..."
python scripts/expansion/generate_massive.py
echo ""

# Étape 3: Validation BioBERT
echo "🔬 ÉTAPE 3/4 : Validation BioBERT..."
python scripts/expansion/validate_massive.py
echo ""

# Étape 4: Fusion avec existant
echo "🔀 ÉTAPE 4/4 : Fusion corpus..."
python scripts/expansion/merge_with_existing.py
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✅ PIPELINE TERMINÉ"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Résultats dans:"
echo "   • src/data/questions/compiled_expanded.json"
echo ""
echo "🎯 Prochaine étape:"
echo "   • Vérifier le corpus expansé"
echo "   • Déployer si satisfait"
echo "   • Mise à jour production"
echo ""
echo "═══════════════════════════════════════════════════════════"

