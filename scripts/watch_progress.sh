#!/bin/bash
# Monitoring SIMPLE avec % et barre de progression

PROGRESS="/Users/valentingaludec/IADE NEW/logs/incremental_progress.json"
LOG="/Users/valentingaludec/IADE NEW/logs/incremental.log"

while true; do
    clear
    echo "============================================================"
    echo "  GÉNÉRATION INCRÉMENTALE - SUIVI EN TEMPS RÉEL"
    echo "============================================================"
    echo ""
    
    if [ -f "$PROGRESS" ]; then
        # Parse JSON
        batch=$(jq -r '.last_batch // 0' "$PROGRESS" 2>/dev/null)
        total=$(jq -r '.total_batches // 6' "$PROGRESS" 2>/dev/null)
        qcms=$(jq -r '.all_qcms | length' "$PROGRESS" 2>/dev/null)
        last_update=$(jq -r '.last_update' "$PROGRESS" 2>/dev/null)
        
        # Calcul %
        if [ "$total" -gt 0 ]; then
            percent=$((batch * 100 / total))
        else
            percent=0
        fi
        
        # Barre de progression (50 caractères)
        filled=$((percent / 2))
        empty=$((50 - filled))
        
        echo "📊 PROGRESSION GLOBALE"
        echo ""
        printf "  ["
        printf "%${filled}s" | tr ' ' '█'
        printf "%${empty}s" | tr ' ' '░'
        printf "] ${percent}%%\n"
        echo ""
        
        echo "📈 STATISTIQUES"
        echo ""
        echo "  Batch actuel     : $batch / $total"
        echo "  Progression      : $percent%"
        echo "  QCM générés      : $qcms"
        echo ""
        
        # Projection
        if [ "$batch" -gt 0 ]; then
            qcms_per_batch=$((qcms / batch))
            projection=$((qcms_per_batch * total))
            echo "  📊 Projection    : ~$projection QCM au total"
            echo ""
        fi
        
        echo "  ⏱️  Dernière MAJ  : $last_update"
        echo ""
        
        # Objectif
        echo "🎯 OBJECTIF v1"
        echo ""
        if [ "$qcms" -ge 1000 ]; then
            echo "  ✅ $qcms / 1000 QCM (ATTEINT !)"
        else
            remaining=$((1000 - qcms))
            echo "  ⏳ $qcms / 1000 QCM ($remaining restants)"
        fi
        
        echo ""
        echo "============================================================"
        echo "  LOGS RÉCENTS"
        echo "============================================================"
        echo ""
        
        if [ -f "$LOG" ]; then
            tail -8 "$LOG" | grep -E "\[|✓|✗|📊|🔧|⚠️|✅"
        fi
        
    else
        echo "⏳ INITIALISATION EN COURS..."
        echo ""
        echo "Le système se prépare..."
        echo ""
        
        # Affiche les premiers logs si disponibles
        if [ -f "$LOG" ]; then
            echo "Logs de démarrage:"
            tail -10 "$LOG"
        fi
    fi
    
    echo ""
    echo "============================================================"
    echo "  Refresh automatique (5 sec) • Ctrl+C pour quitter"
    echo "============================================================"
    
    sleep 5
done

