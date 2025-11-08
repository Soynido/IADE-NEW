#!/bin/bash
# Affiche les QCM au fur et à mesure de la génération

PROGRESS="/Users/valentingaludec/IADE NEW/logs/incremental_progress.json"

echo "============================================================"
echo "  APERÇU QCM GÉNÉRÉS - LIVE"
echo "============================================================"
echo ""
echo "⏳ Attente du premier batch..."
echo ""

last_count=0

while true; do
    if [ -f "$PROGRESS" ]; then
        # Compte actuel de QCM
        current=$(jq -r '.all_qcms | length' "$PROGRESS" 2>/dev/null || echo "0")
        
        if [ "$current" -gt "$last_count" ]; then
            clear
            echo "============================================================"
            echo "  APERÇU QCM GÉNÉRÉS - LIVE ($current QCM)"
            echo "============================================================"
            echo ""
            
            # Affiche les 5 derniers QCM
            jq -r '.all_qcms[-5:] | to_entries[] | "
┌────────────────────────────────────────────────────────────┐
│ QCM #\(.key + 1) - Module: \(.value.module_id)
├────────────────────────────────────────────────────────────┤
│ 📝 \(.value.text[:70])...
│
│ Options:
│   A) \(.value.options[0][:50])
│   B) \(.value.options[1][:50])
│   C) \(.value.options[2][:50])
│   D) \(.value.options[3][:50])
│
│ ✅ Réponse correcte: \(["A","B","C","D"][.value.correctAnswer])
│
│ 💡 Explication: \(.value.explanation[:80])...
└────────────────────────────────────────────────────────────┘
"' "$PROGRESS" 2>/dev/null
            
            echo ""
            echo "📊 Total: $current QCM générés"
            echo "🔄 Mise à jour automatique..."
            
            last_count=$current
        fi
    fi
    
    sleep 10
done

