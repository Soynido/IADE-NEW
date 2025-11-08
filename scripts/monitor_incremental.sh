#!/bin/bash
# Monitoring génération incrémentale

PROGRESS="/Users/valentingaludec/IADE NEW/logs/incremental_progress.json"
LOG="/Users/valentingaludec/IADE NEW/logs/incremental.log"

while true; do
    clear
    echo "============================================================"
    echo "  GÉNÉRATION INCRÉMENTALE - MONITORING"
    echo "============================================================"
    echo ""
    
    if [ -f "$PROGRESS" ]; then
        batch=$(jq -r '.last_batch // 0' "$PROGRESS" 2>/dev/null || echo "0")
        total=$(jq -r '.total_batches // 9' "$PROGRESS" 2>/dev/null || echo "9")
        qcms=$(jq -r '.all_qcms | length' "$PROGRESS" 2>/dev/null || echo "0")
        
        percent=$((batch * 100 / total))
        
        echo "📊 PROGRESSION"
        echo ""
        echo "  Batch actuel   : $batch / $total"
        echo "  Progression    : $percent%"
        echo "  QCM générés    : $qcms"
        echo ""
        
        # Barre
        filled=$((percent / 2))
        empty=$((50 - filled))
        printf "  ["
        printf "%${filled}s" | tr ' ' '█'
        printf "%${empty}s" | tr ' ' '░'
        printf "] $percent%%\n"
        
        echo ""
        echo "============================================================"
        echo "  LOGS RÉCENTS (10 dernières lignes)"
        echo "============================================================"
        echo ""
        
        if [ -f "$LOG" ]; then
            tail -10 "$LOG"
        else
            echo "  Aucun log pour l'instant..."
        fi
    else
        echo "⏳ Démarrage en cours..."
        echo ""
        echo "Le fichier de progression sera créé au 1er batch."
    fi
    
    echo ""
    echo "============================================================"
    echo "  Refresh automatique dans 10 sec (Ctrl+C pour quitter)"
    echo "============================================================"
    
    sleep 10
done

