#!/bin/bash
# Monitoring génération séquentielle

PROGRESS="/Users/valentingaludec/IADE NEW/logs/sequential_progress.json"
LOG="/Users/valentingaludec/IADE NEW/logs/sequential.log"

while true; do
    clear
    echo "============================================================"
    echo "  GÉNÉRATION SÉQUENTIELLE - MONITORING"
    echo "============================================================"
    echo ""
    
    if [ -f "$PROGRESS" ]; then
        idx=$(jq -r '.last_idx // 0' "$PROGRESS" 2>/dev/null)
        qcms=$(jq -r '.qcms | length' "$PROGRESS" 2>/dev/null)
        success=$(jq -r '.stats.success // 0' "$PROGRESS" 2>/dev/null)
        failed=$(jq -r '.stats.failed // 0' "$PROGRESS" 2>/dev/null)
        
        total=297
        percent=$((idx * 100 / total))
        
        # Barre progression
        filled=$((percent / 2))
        empty=$((50 - filled))
        
        echo "📊 PROGRESSION"
        echo ""
        printf "  ["
        printf "%${filled}s" | tr ' ' '█'
        printf "%${empty}s" | tr ' ' '░'
        printf "] ${percent}%%\n"
        echo ""
        
        echo "📈 STATISTIQUES"
        echo ""
        echo "  Chunks traités  : $idx / $total"
        echo "  QCM générés     : $qcms"
        echo "  Succès          : $success"
        echo "  Échecs          : $failed"
        
        if [ "$idx" -gt 0 ]; then
            success_rate=$((success * 100 / idx))
            qcms_per_chunk=$((qcms / success))
            projection=$((qcms_per_chunk * total))
            
            echo "  Taux succès     : ${success_rate}%"
            echo ""
            echo "  📊 Projection   : ~$projection QCM au total"
        fi
        
        echo ""
        echo "============================================================"
        echo "  LOGS RÉCENTS"
        echo "============================================================"
        echo ""
        
        if [ -f "$LOG" ]; then
            tail -8 "$LOG"
        fi
        
    else
        echo "⏳ INITIALISATION..."
        echo ""
        
        if [ -f "$LOG" ]; then
            tail -5 "$LOG"
        else
            echo "Démarrage en cours..."
        fi
    fi
    
    echo ""
    echo "============================================================"
    echo "  Refresh 5 sec • Ctrl+C pour quitter (génération continue)"
    echo "============================================================"
    
    sleep 5
done

