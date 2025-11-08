#!/bin/bash
#
# Script de monitoring de la génération avec refresh auto (5 sec)
# 
# Usage: bash scripts/monitor_generation.sh
#

PROGRESS_FILE="/Users/valentingaludec/IADE NEW/logs/generation_progress.json"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher la barre de progression
progress_bar() {
    local percent=$1
    local width=50
    local completed=$((percent * width / 100))
    local remaining=$((width - completed))
    
    printf "["
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "]"
}

while true; do
    clear
    echo "============================================================"
    echo "  IADE NEW - MONITORING GÉNÉRATION QCM (Refresh: 5 sec)"
    echo "============================================================"
    echo ""
    
    if [ -f "$PROGRESS_FILE" ]; then
        # Parse JSON avec jq
        total=$(jq -r '.total_chunks' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        completed=$(jq -r '.completed_chunks' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        successful=$(jq -r '.successful_chunks' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        failed=$(jq -r '.failed_chunks' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        qcms=$(jq -r '.qcms_generated' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        percent=$(jq -r '.progress_percent' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        success_rate=$(jq -r '.success_rate' "$PROGRESS_FILE" 2>/dev/null || echo "0")
        last_update=$(jq -r '.last_update' "$PROGRESS_FILE" 2>/dev/null || echo "N/A")
        
        # Arrondi pourcentages
        percent_int=${percent%.*}
        success_rate_int=${success_rate%.*}
        
        # Progression
        echo -e "${BLUE}PROGRESSION GLOBALE${NC}"
        echo ""
        printf "  "
        progress_bar $percent_int
        printf " ${GREEN}${percent_int}%%${NC}\n"
        echo ""
        
        # Stats
        echo -e "${BLUE}STATISTIQUES${NC}"
        echo ""
        echo -e "  Total chunks     : ${GREEN}$total${NC}"
        echo -e "  Chunks traités   : ${YELLOW}$completed${NC} / $total"
        echo -e "  Chunks réussis   : ${GREEN}$successful${NC}"
        echo -e "  Chunks échoués   : ${RED}$failed${NC}"
        echo -e "  Taux succès      : ${GREEN}${success_rate_int}%${NC}"
        echo ""
        echo -e "  ${GREEN}🎯 QCM GÉNÉRÉS : $qcms${NC}"
        echo ""
        
        # Estimation temps restant
        if [ "$completed" -gt 0 ] && [ "$total" -gt 0 ]; then
            remaining=$((total - completed))
            
            # Temps moyen par chunk (estimation : 1 min avec parallélisation)
            avg_time_per_chunk=1  # min
            eta_minutes=$((remaining * avg_time_per_chunk / 4))  # Divisé par 4 workers
            eta_hours=$((eta_minutes / 60))
            eta_mins=$((eta_minutes % 60))
            
            echo -e "${BLUE}ESTIMATION${NC}"
            echo ""
            echo -e "  Restant          : $remaining chunks"
            echo -e "  ETA              : ~${eta_hours}h ${eta_mins}min"
            echo ""
        fi
        
        # Objectifs
        echo -e "${BLUE}OBJECTIFS V1${NC}"
        echo ""
        
        if [ "$qcms" -ge 2500 ]; then
            echo -e "  QCM ≥ 2500       : ${GREEN}✓ ATTEINT ($qcms)${NC}"
        elif [ "$qcms" -ge 2000 ]; then
            echo -e "  QCM ≥ 2000       : ${YELLOW}✓ PROCHE ($qcms)${NC}"
        else
            echo -e "  QCM ≥ 2500       : ${RED}⏳ En cours ($qcms / 2500)${NC}"
        fi
        
        echo ""
        echo -e "  Dernière MAJ     : $last_update"
        
    else
        echo "⏳ Génération pas encore démarrée ou fichier de progression introuvable"
        echo ""
        echo "Fichier attendu : $PROGRESS_FILE"
    fi
    
    echo ""
    echo "============================================================"
    echo "  Appuyez sur Ctrl+C pour quitter (génération continue)"
    echo "============================================================"
    
    sleep 5
done

