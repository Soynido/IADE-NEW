/**
 * Service API - Envoi feedback vers Redis Upstash
 * Implémente la spec.md Section X : Redis optionnel (Upstash)
 * 
 * Fonctionnalités:
 * - Push feedback en arrière-plan (non bloquant)
 * - Gestion silencieuse des erreurs
 * - Pas critique pour fonctionnement app
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

// Support des variables Vercel (KV_*) et locales (VITE_*)
const REDIS_URL = 
  import.meta.env.VITE_KV_REST_API_URL || 
  import.meta.env.VITE_UPSTASH_REDIS_REST_URL ||
  import.meta.env.KV_REST_API_URL;

const REDIS_TOKEN = 
  import.meta.env.VITE_KV_REST_API_TOKEN || 
  import.meta.env.VITE_UPSTASH_REDIS_REST_TOKEN ||
  import.meta.env.KV_REST_API_TOKEN;

// Active uniquement si variables d'environnement définies
const REDIS_ENABLED = Boolean(REDIS_URL && REDIS_TOKEN);

// Debug: affiche le statut Redis au chargement
if (typeof window !== 'undefined') {
  console.info('[Feedback] Redis Upstash:', REDIS_ENABLED ? '✅ Activé' : '⚠️ Désactivé (local uniquement)');
  if (REDIS_ENABLED && REDIS_URL) {
    console.info('[Feedback] Redis URL:', REDIS_URL);
  }
}

// =============================================================================
// TYPES
// =============================================================================

interface FeedbackPayload {
  questionId: string;
  score: 1 | 2 | 3;
  timestamp: string;
}

// =============================================================================
// SERVICE API
// =============================================================================

/**
 * Envoie le feedback vers Redis Upstash (non bloquant)
 * Si échec : log console uniquement, pas d'erreur utilisateur
 */
export async function sendFeedbackToRedis(
  questionId: string,
  score: 1 | 2 | 3
): Promise<void> {
  // Si Redis désactivé, retour silencieux
  if (!REDIS_ENABLED) {
    console.info('[Feedback] Redis non configuré, stockage local uniquement');
    return;
  }

  try {
    const payload: FeedbackPayload = {
      questionId,
      score,
      timestamp: new Date().toISOString()
    };

    // Upstash REST API : LPUSH pour ajouter à une liste
    const response = await fetch(`${REDIS_URL}/lpush/feedback:${questionId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.warn('[Feedback] Échec envoi Redis:', response.status);
      return;
    }

    // Optionnel : expiration après 90 jours (aligné avec localStorage)
    await fetch(`${REDIS_URL}/expire/feedback:${questionId}/7776000`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });

    console.info('[Feedback] ✅ Envoyé vers Redis:', questionId, 'score:', score);
  } catch (error) {
    // Erreur silencieuse (non bloquante)
    console.warn('[Feedback] Erreur Redis (ignorée):', error);
  }
}

/**
 * Récupère les feedbacks d'une question depuis Redis (optionnel)
 * Utilisé pour analyse globale côté admin
 */
export async function getFeedbackFromRedis(
  questionId: string
): Promise<FeedbackPayload[]> {
  if (!REDIS_ENABLED) {
    return [];
  }

  try {
    const response = await fetch(`${REDIS_URL}/lrange/feedback:${questionId}/0/-1`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    return data.result || [];
  } catch (error) {
    console.warn('[Feedback] Erreur lecture Redis:', error);
    return [];
  }
}

/**
 * Récupère les statistiques globales de feedback (admin)
 */
export async function getFeedbackStats(): Promise<Record<string, number>> {
  if (!REDIS_ENABLED) {
    return {};
  }

  try {
    // Récupère toutes les clés feedback:*
    const response = await fetch(`${REDIS_URL}/keys/feedback:*`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });

    if (!response.ok) {
      return {};
    }

    const data = await response.json();
    const keys = data.result || [];

    // Compte les feedbacks par questionId
    const stats: Record<string, number> = {};
    for (const key of keys) {
      const questionId = key.replace('feedback:', '');
      
      const countResponse = await fetch(`${REDIS_URL}/llen/${key}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${REDIS_TOKEN}`
        }
      });

      if (countResponse.ok) {
        const countData = await countResponse.json();
        stats[questionId] = countData.result || 0;
      }
    }

    return stats;
  } catch (error) {
    console.warn('[Feedback] Erreur stats Redis:', error);
    return {};
  }
}

// =============================================================================
// EXPORT
// =============================================================================

export default {
  sendFeedbackToRedis,
  getFeedbackFromRedis,
  getFeedbackStats
};

