#!/bin/bash

# Script pour configurer les variables d'environnement Vercel via CLI
# Usage: ./scripts/setup_vercel_env.sh

echo "═══════════════════════════════════════════════════════════"
echo "🔧 CONFIGURATION VERCEL - Variables d'environnement"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Variables à configurer
VARS=(
  "KV_REST_API_URL:https://full-crab-26762.upstash.io"
  "KV_REST_API_TOKEN:AWiKAAIncDI0ZWFhNDNjYzA0N2I0NmI4YTQ0ZjU5OGJiNGY4OGY3YnAyMjY3NjI"
  "UPSTASH_REDIS_REST_URL:https://full-crab-26762.upstash.io"
  "UPSTASH_REDIS_REST_TOKEN:AWiKAAIncDI0ZWFhNDNjYzA0N2I0NmI4YTQ0ZjU5OGJiNGY4OGY3YnAyMjY3NjI"
)

echo "📝 Configuration via Dashboard Vercel (recommandé) :"
echo ""
echo "1. Aller sur https://vercel.com/valentin-galudec-s-projects/iade-new"
echo "2. Settings → Environment Variables"
echo "3. Ajouter les variables suivantes :"
echo ""

for var in "${VARS[@]}"; do
  KEY="${var%%:*}"
  VALUE="${var#*:}"
  echo "   • $KEY = $VALUE"
done

echo ""
echo "4. Scope : Production + Preview + Development"
echo "5. Save et redéployer"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "OU via CLI (interactif) :"
echo ""

for var in "${VARS[@]}"; do
  KEY="${var%%:*}"
  VALUE="${var#*:}"
  echo "vercel env add $KEY production"
  echo "# Entrer : $VALUE"
  echo ""
done

echo "═══════════════════════════════════════════════════════════"

