#!/bin/bash

# Script de monitoring Phase 12

clear

echo "═══════════════════════════════════════════════════════════"
echo "📊 MONITORING PHASE 12 - EXPANSION MASSIVE"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Fonction pour afficher la progression
show_progress() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🕐 $(date '+%H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Vérifie les fichiers générés
    if [ -f "src/data/raw/pages_metadata.json" ]; then
        PAGES=$(cat src/data/raw/pages_metadata.json 2>/dev/null | grep -o '"total_pages": [0-9]*' | grep -o '[0-9]*')
        echo "✅ Étape 1 : Extraction"
        echo "   → $PAGES pages extraites"
        echo ""
    fi
    
    if [ -f "src/data/questions/generated_massive.json" ]; then
        GEN_COUNT=$(cat src/data/questions/generated_massive.json 2>/dev/null | grep -o '"id":' | wc -l | tr -d ' ')
        echo "✅ Étape 2 : Génération"
        echo "   → $GEN_COUNT QCM générés"
        echo ""
    fi
    
    if [ -f "src/data/questions/validated_massive.json" ]; then
        VAL_COUNT=$(cat src/data/questions/validated_massive.json 2>/dev/null | grep -o '"id":' | wc -l | tr -d ' ')
        echo "✅ Étape 3 : Validation BioBERT"
        echo "   → $VAL_COUNT QCM validés"
        echo ""
    fi
    
    if [ -f "src/data/questions/compiled_expanded.json" ]; then
        FINAL_COUNT=$(cat src/data/questions/compiled_expanded.json 2>/dev/null | grep -o '"id":' | wc -l | tr -d ' ')
        echo "✅ Étape 4 : Fusion"
        echo "   → $FINAL_COUNT QCM au total"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 PHASE 12 TERMINÉE !"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if [ -f "src/data/questions/expansion_summary.txt" ]; then
            echo ""
            cat src/data/questions/expansion_summary.txt
        fi
        
        exit 0
    fi
    
    # Affiche les dernières lignes du log
    if [ -f "logs/pipeline.log" ]; then
        echo "📝 Dernières activités :"
        echo ""
        tail -n 5 logs/pipeline.log | sed 's/^/   /'
        echo ""
    fi
    
    if [ -f "logs/phase12_execution.log" ]; then
        echo "📋 Dernière ligne d'exécution :"
        echo ""
        tail -n 1 logs/phase12_execution.log | sed 's/^/   /'
        echo ""
    fi
}

# Boucle de monitoring (refresh toutes les 5 secondes)
while true; do
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "📊 MONITORING PHASE 12 - EXPANSION MASSIVE"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    show_progress
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏱️  Refresh automatique dans 5 secondes..."
    echo "   (Ctrl+C pour quitter)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    sleep 5
done

