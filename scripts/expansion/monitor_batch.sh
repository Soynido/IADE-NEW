#!/bin/bash

# Script de monitoring pour génération par batch

BATCH_NUM=${1:-1}
LOG_FILE="logs/batch_${BATCH_NUM}.log"

clear

echo "═══════════════════════════════════════════════════════════"
echo "📊 MONITORING BATCH $BATCH_NUM - Phase 12"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Fonction pour afficher la progression
show_progress() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🕐 $(date '+%H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Vérifie si le log existe
    if [ ! -f "$LOG_FILE" ]; then
        echo "⏳ Batch $BATCH_NUM en cours de démarrage..."
        return
    fi
    
    # Affiche les dernières lignes de progression
    echo "📋 Dernière progression :"
    echo ""
    tail -n 1 "$LOG_FILE" | grep "Progression:" | sed 's/^/   /'
    echo ""
    
    # Compte les QCM générés
    if [ -f "src/data/questions/generated_massive.json" ]; then
        QCM_COUNT=$(cat src/data/questions/generated_massive.json 2>/dev/null | grep -o '"id":' | wc -l | tr -d ' ')
        echo "📊 QCM générés : $QCM_COUNT"
        echo ""
    fi
    
    # Vérifie si batch terminé
    if grep -q "✅ BATCH $BATCH_NUM TERMINÉ" "$LOG_FILE" 2>/dev/null; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 BATCH $BATCH_NUM TERMINÉ !"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Affiche le résumé
        if [ -f "src/data/questions/expansion_summary.txt" ]; then
            cat src/data/questions/expansion_summary.txt
        fi
        
        # Indique le prochain batch
        if [ $BATCH_NUM -lt 4 ]; then
            NEXT_BATCH=$((BATCH_NUM + 1))
            echo ""
            echo "🎯 Pour lancer le batch suivant :"
            echo "   bash scripts/expansion/run_batch.sh $NEXT_BATCH"
        fi
        
        exit 0
    fi
    
    # Affiche les dernières lignes du log
    echo "📝 Dernières activités :"
    echo ""
    tail -n 5 "$LOG_FILE" | sed 's/^/   /'
    echo ""
}

# Boucle de monitoring (refresh toutes les 10 secondes)
while true; do
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "📊 MONITORING BATCH $BATCH_NUM - Phase 12"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    show_progress
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏱️  Refresh automatique dans 10 secondes..."
    echo "   (Ctrl+C pour quitter)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    sleep 10
done

