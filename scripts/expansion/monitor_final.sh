#!/bin/bash

# Monitoring simplifié pour les 3 batchs restants

LOG_FILE="logs/batches_2_3_4.log"

clear

echo "═══════════════════════════════════════════════════════════"
echo "📊 MONITORING BATCHS 2, 3 & 4 - Complétion finale"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Fonction pour afficher l'état
show_status() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🕐 $(date '+%H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Vérifie le log
    if [ ! -f "$LOG_FILE" ]; then
        echo "⏳ Démarrage en cours..."
        return
    fi
    
    # Détecte quel batch est en cours
    if grep -q "🔄 BATCH 2" "$LOG_FILE" && ! grep -q "✅ Batch 2 terminé" "$LOG_FILE"; then
        CURRENT="BATCH 2 (30-60)"
        STATUS="🔄 En cours"
    elif grep -q "✅ Batch 2 terminé" "$LOG_FILE" && ! grep -q "🔄 BATCH 3" "$LOG_FILE"; then
        CURRENT="BATCH 2 → BATCH 3"
        STATUS="⏳ Transition"
    elif grep -q "🔄 BATCH 3" "$LOG_FILE" && ! grep -q "✅ Batch 3 terminé" "$LOG_FILE"; then
        CURRENT="BATCH 3 (60-90)"
        STATUS="🔄 En cours"
    elif grep -q "✅ Batch 3 terminé" "$LOG_FILE" && ! grep -q "🔄 BATCH 4" "$LOG_FILE"; then
        CURRENT="BATCH 3 → BATCH 4"
        STATUS="⏳ Transition"
    elif grep -q "🔄 BATCH 4" "$LOG_FILE" && ! grep -q "✅ Batch 4 terminé" "$LOG_FILE"; then
        CURRENT="BATCH 4 (90-124)"
        STATUS="🔄 En cours"
    elif grep -q "✅ Batch 4 terminé" "$LOG_FILE"; then
        CURRENT="TOUS LES BATCHS"
        STATUS="✅ TERMINÉS"
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 EXPANSION COMPLÈTE TERMINÉE !"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Affiche le résumé
        if [ -f "src/data/questions/expansion_summary.txt" ]; then
            cat src/data/questions/expansion_summary.txt
        fi
        
        exit 0
    else
        CURRENT="Démarrage"
        STATUS="⏳"
    fi
    
    echo "📦 Batch actuel : $CURRENT"
    echo "📊 Status : $STATUS"
    echo ""
    
    # Compte les QCM
    if [ -f "src/data/questions/compiled_expanded.json" ]; then
        QCM_COUNT=$(cat src/data/questions/compiled_expanded.json 2>/dev/null | grep -o '"id":' | wc -l | tr -d ' ')
        echo "📈 QCM total : $QCM_COUNT"
        echo ""
    fi
    
    # Affiche la dernière progression
    echo "📝 Dernière progression :"
    echo ""
    tail -n 1 "$LOG_FILE" | grep "Progression:" | sed 's/^/   /' || echo "   En traitement..."
    echo ""
}

# Boucle de monitoring
while true; do
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "📊 MONITORING BATCHS 2, 3 & 4 - Complétion finale"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    show_status
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏱️  Refresh dans 15 secondes..."
    echo "   (Ctrl+C pour quitter)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    sleep 15
done

