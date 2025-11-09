#!/bin/bash

# Script pour exécuter un batch spécifique de génération
# Usage: ./run_batch.sh <batch_num>
# Exemple: ./run_batch.sh 1

set -e

BATCH_NUM=$1

if [ -z "$BATCH_NUM" ]; then
    echo "❌ Usage: ./run_batch.sh <batch_num>"
    echo "   Batchs disponibles: 1, 2, 3, 4"
    exit 1
fi

cd "$(dirname "$0")/../.."

# Définition des ranges
case $BATCH_NUM in
    1)
        START=0
        END=30
        ;;
    2)
        START=30
        END=60
        ;;
    3)
        START=60
        END=90
        ;;
    4)
        START=90
        END=124
        ;;
    *)
        echo "❌ Batch invalide. Utilisez 1, 2, 3 ou 4"
        exit 1
        ;;
esac

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     🚀 BATCH $BATCH_NUM - PAGES [$START:$END]                          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Activer environnement
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    exit 1
fi

source venv/bin/activate

echo "✅ Environnement activé"
echo ""

# ÉTAPE 1: Génération
echo "============================================================"
echo "⚡ GÉNÉRATION - Batch $BATCH_NUM (pages $START-$END)"
echo "============================================================"
python scripts/expansion/generate_massive_optimized.py --range $START $END

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la génération"
    exit 1
fi

echo ""

# ÉTAPE 2: Validation BioBERT
echo "============================================================"
echo "🔬 VALIDATION BioBERT"
echo "============================================================"
python scripts/expansion/validate_massive.py

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la validation"
    exit 1
fi

echo ""

# ÉTAPE 3: Fusion avec corpus existant
echo "============================================================"
echo "🔀 FUSION AVEC CORPUS EXISTANT"
echo "============================================================"
python scripts/expansion/merge_with_existing.py

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la fusion"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     ✅ BATCH $BATCH_NUM TERMINÉ                                ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Afficher résumé si disponible
if [ -f "src/data/questions/expansion_summary.txt" ]; then
    cat src/data/questions/expansion_summary.txt
fi

# Indiquer le prochain batch
if [ $BATCH_NUM -lt 4 ]; then
    NEXT_BATCH=$((BATCH_NUM + 1))
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 PROCHAIN BATCH:"
    echo "   bash scripts/expansion/run_batch.sh $NEXT_BATCH"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 TOUS LES BATCHS TERMINÉS !"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

