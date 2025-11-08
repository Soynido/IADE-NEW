#!/bin/bash

LOG_FILE="logs/optimize_phrasing.log"
PID_FILE="logs/optimize_phrasing.pid"

echo "═══════════════════════════════════════════════════════════"
echo "📊 MONITORING OPTIMISATION LINGUISTIQUE v1.2"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Vérifie si le processus tourne
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✓ Processus actif (PID: $PID)"
    else
        echo "✓ Processus terminé"
    fi
else
    echo "⚠️  PID non trouvé"
fi

echo ""
echo "───────────────────────────────────────────────────────────"
echo "📝 PROGRESSION (dernières lignes)"
echo "───────────────────────────────────────────────────────────"
echo ""

if [ -f "$LOG_FILE" ]; then
    tail -n 20 "$LOG_FILE"
else
    echo "⚠️  Log non trouvé: $LOG_FILE"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

