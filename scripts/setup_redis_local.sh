#!/bin/bash

# =============================================================================
# Script de configuration Redis Upstash pour développement local
# =============================================================================

echo "🔧 Configuration Redis Upstash pour IADE NEW"
echo ""

# Credentials Upstash
REDIS_REST_URL="https://full-crab-26762.upstash.io"
REDIS_TOKEN="AWiKAAIncDI0ZWFhNDNjYzA0N2I0NmI4YTQ0ZjU5OGJiNGY4OGY3YnAyMjY3NjI"
REDIS_URL_FULL="rediss://default:${REDIS_TOKEN}@full-crab-26762.upstash.io:6379"

# Créer .env.local
cat > .env.local << EOF
# IADE NEW - Variables d'environnement locales
# NE PAS COMMITTER CE FICHIER (déjà dans .gitignore)

# =============================================================================
# REDIS UPSTASH - Feedback utilisateur
# =============================================================================
# Source: https://console.upstash.com/redis/full-crab-26762

# Variables Vercel (nomenclature KV_*)
VITE_KV_REST_API_URL=${REDIS_REST_URL}
VITE_KV_REST_API_TOKEN=${REDIS_TOKEN}

# Alternatives (compatibilité)
VITE_UPSTASH_REDIS_REST_URL=${REDIS_REST_URL}
VITE_UPSTASH_REDIS_REST_TOKEN=${REDIS_TOKEN}

# Redis URL complète (pour scripts Python si nécessaire)
REDIS_URL=${REDIS_URL_FULL}

# Note: Le système fonctionne sans Redis (stockage localStorage uniquement)
# Redis est utilisé uniquement pour l'agrégation globale des feedbacks
EOF

echo "✅ Fichier .env.local créé avec succès"
echo ""
echo "📋 Configuration Redis:"
echo "   URL: ${REDIS_REST_URL}"
echo "   Token: ${REDIS_TOKEN:0:20}..."
echo ""
echo "🚀 Prochaines étapes:"
echo "   1. Redémarrer le serveur de développement:"
echo "      npm run dev"
echo ""
echo "   2. Tester un feedback dans l'application"
echo ""
echo "   3. Vérifier les logs console:"
echo "      [Feedback] Redis Upstash: ✅ Activé"
echo ""
echo "   4. Vérifier Redis Console:"
echo "      https://console.upstash.com/redis/full-crab-26762"
echo ""

