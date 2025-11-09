#!/bin/bash

# Script pour lancer tous les batchs restants (2, 3, 4) séquentiellement

set -e

cd "$(dirname "$0")/../.."

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     🚀 LANCEMENT BATCHS 2, 3 & 4 - COMPLÉTION          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Activer environnement
source venv/bin/activate

# BATCH 2 (pages 30-60)
echo "════════════════════════════════════════════════════════════"
echo "🔄 BATCH 2 - Pages 30-60"
echo "════════════════════════════════════════════════════════════"
python scripts/expansion/generate_massive_optimized.py --range 30 60
python scripts/expansion/validate_massive.py
python scripts/expansion/merge_with_existing.py
echo "✅ Batch 2 terminé"
echo ""

# BATCH 3 (pages 60-90)
echo "════════════════════════════════════════════════════════════"
echo "🔄 BATCH 3 - Pages 60-90"
echo "════════════════════════════════════════════════════════════"
python scripts/expansion/generate_massive_optimized.py --range 60 90
python scripts/expansion/validate_massive.py
python scripts/expansion/merge_with_existing.py
echo "✅ Batch 3 terminé"
echo ""

# BATCH 4 (pages 90-124)
echo "════════════════════════════════════════════════════════════"
echo "🔄 BATCH 4 - Pages 90-124"
echo "════════════════════════════════════════════════════════════"
python scripts/expansion/generate_massive_optimized.py --range 90 124
python scripts/expansion/validate_massive.py
python scripts/expansion/merge_with_existing.py
echo "✅ Batch 4 terminé"
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     🎉 TOUS LES BATCHS TERMINÉS !                       ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Afficher résumé final
if [ -f "src/data/questions/expansion_summary.txt" ]; then
    echo "📊 RÉSUMÉ FINAL:"
    echo ""
    cat src/data/questions/expansion_summary.txt
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎯 PROCHAINES ÉTAPES:"
echo "════════════════════════════════════════════════════════════"
echo "1. Régénérer examens blancs"
echo "2. Tester modes pédagogiques"
echo "3. Déployer v2.0 sur Vercel"
echo "════════════════════════════════════════════════════════════"

