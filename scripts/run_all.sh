#!/bin/bash
#
# Pipeline complet IADE NEW - Génération QCM
# Tâche [086-086b] - Phase 9 : QA & Polish
#
# Usage:
#   bash scripts/run_all.sh              # Full run (tous modules)
#   bash scripts/run_all.sh --subset 10  # Dry run (10 modules)
#

set -e  # Arrêt si erreur

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT="/Users/valentingaludec/IADE NEW"
VENV_PATH="$PROJECT_ROOT/venv"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

log_step() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# =============================================================================
# PIPELINE
# =============================================================================

main() {
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"
    
    echo "============================================================"
    echo "PIPELINE COMPLET IADE NEW"
    echo "============================================================"
    echo "Début: $(date)"
    echo ""
    
    # Phase 1: Extraction PDF
    log_step "Phase 1: Extraction PDF..."
    python scripts/extract_pdfs.py \
        --input "src/data/sources/*.pdf" \
        --out src/data/modules/ \
        --metadata src/data/metadata.json
    
    # Phase 2: Indexation
    log_step "Phase 2: Indexation TF-IDF..."
    python scripts/index_chunks.py \
        --modules src/data/modules/ \
        --out src/data/keywords.json
    
    log_step "Phase 2: Analyse annales..."
    python scripts/analyze_annales.py \
        --annales "src/data/sources/annalescorrigées-*.pdf" \
        --out src/data/annales_profile.json
    
    # Phase 3: Génération QCM
    log_step "Phase 3: Génération QCM (LONG - plusieurs heures)..."
    python scripts/ai_generation/generate_batch.py \
        --modules src/data/modules/ \
        --keywords src/data/keywords.json \
        --profile src/data/annales_profile.json \
        --out src/data/questions/generated_raw.json \
        --model mistral:latest \
        --per-chunk 3
    
    # Phase 4: Validation BioBERT
    log_step "Phase 4: Validation BioBERT..."
    python scripts/ai_generation/biobert_client.py \
        --in src/data/questions/generated_raw.json \
        --out src/data/questions/generated_biobert.json \
        --metadata src/data/metadata.json
    
    # Phase 4: Validation Sémantique
    log_step "Phase 4: Validation sémantique..."
    python scripts/ai_generation/semantic_validator.py \
        --in src/data/questions/generated_biobert.json \
        --modules src/data/modules/ \
        --keywords src/data/keywords.json \
        --out src/data/questions/generated_scored.json
    
    # Phase 5: Consolidation
    log_step "Phase 5: Validation finale..."
    python scripts/ai_generation/validate_all.py \
        --in src/data/questions/generated_scored.json \
        --out src/data/questions/validated.json
    
    log_step "Phase 5: Classification modes..."
    python scripts/ai_generation/classify_modes.py \
        --in src/data/questions/validated.json \
        --out-dir src/data/questions/
    
    # Phase 5: Rapports
    log_step "Phase 5: Génération rapports..."
    python scripts/reports/coverage_report.py \
        --modules src/data/modules/ \
        --questions src/data/questions/validated.json \
        --out docs/coverage_report.md
    
    echo ""
    echo "============================================================"
    log_step "✅ PIPELINE COMPLET TERMINÉ"
    echo "============================================================"
    echo "Fin: $(date)"
    echo ""
    echo "Fichiers générés:"
    echo "  - src/data/questions/revision.json"
    echo "  - src/data/questions/entrainement.json"
    echo "  - src/data/questions/concours.json"
    echo "  - src/data/questions/compiled.json"
    echo "  - docs/coverage_report.md"
}

# Exécution
main "$@"

