/**
 * Service API - Gestion des rapports de bugs
 * Envoi vers Redis + localStorage pour analyse IA ultérieure
 */

import { BugReport, BugReportFormData, BugReportStats } from '@/types/bugReport';
import { Question } from '@/types';

// =============================================================================
// CONFIGURATION
// =============================================================================

const REDIS_URL = 
  import.meta.env.VITE_KV_REST_API_URL || 
  import.meta.env.VITE_UPSTASH_REDIS_REST_URL ||
  import.meta.env.KV_REST_API_URL;

const REDIS_TOKEN = 
  import.meta.env.VITE_KV_REST_API_TOKEN || 
  import.meta.env.VITE_UPSTASH_REDIS_REST_TOKEN ||
  import.meta.env.KV_REST_API_TOKEN;

const REDIS_ENABLED = Boolean(REDIS_URL && REDIS_TOKEN);

// =============================================================================
// HELPERS
// =============================================================================

function generateBugId(): string {
  return `bug_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function detectDeviceInfo(): string {
  const ua = navigator.userAgent;
  if (/mobile/i.test(ua)) return 'mobile';
  if (/tablet/i.test(ua)) return 'tablet';
  return 'desktop';
}

function estimateSeverity(
  category: string,
  question: Question
): 'low' | 'medium' | 'high' {
  // Sévérité haute : réponse incorrecte, terme médical incorrect
  if (category === 'reponse_incorrecte' || category === 'terme_medical_incorrect') {
    return 'high';
  }
  
  // Sévérité moyenne : question ambiguë, plusieurs réponses, explication incorrecte
  if (category === 'question_ambigue' || 
      category === 'plusieurs_reponses' || 
      category === 'explication_incorrecte') {
    return 'medium';
  }
  
  // Sévérité basse : orthographe, référence, etc.
  return 'low';
}

// =============================================================================
// API PRINCIPALE
// =============================================================================

/**
 * Soumet un rapport de bug
 */
export async function submitBugReport(
  formData: BugReportFormData,
  question: Question,
  mode: 'revision' | 'entrainement' | 'concours',
  userAnswer?: number
): Promise<BugReport> {
  const bugId = generateBugId();
  
  // ✅ v2.0 : Multi-catégories + sévérité maximale
  const maxSeverity = formData.categories
    .map(cat => estimateSeverity(cat, question))
    .sort((a, b) => {
      const order = { high: 3, medium: 2, low: 1 };
      return order[b] - order[a];
    })[0] || 'medium';
  
  const report: BugReport = {
    bugId,
    questionId: question.id || question.chunk_id,
    categories: formData.categories,  // ✅ Plusieurs catégories
    severity: maxSeverity,
    description: formData.description,
    suggestedFix: formData.suggestedFix,
    userAnswer,
    expectedAnswer: formData.expectedAnswer,
    context: {
      mode,
      moduleId: question.module_id || 'unknown',
      timestamp: new Date().toISOString(),
      deviceInfo: detectDeviceInfo()
    },
    status: 'pending',
    createdAt: new Date().toISOString()
  };

  // 1. Sauvegarde localStorage (backup local)
  await saveBugReportLocally(report);
  
  // 2. Envoi Redis (si configuré) - ✅ v2.0 : Par catégorie
  if (REDIS_ENABLED) {
    await sendBugReportToRedis(report);
  }
  
  console.info('[BugReport] ✅ Rapport enregistré:', bugId, 'Catégories:', formData.categories);
  
  return report;
}

/**
 * Sauvegarde locale dans localStorage
 */
async function saveBugReportLocally(report: BugReport): Promise<void> {
  try {
    const storageKey = 'iade_bug_reports_v1';
    const existing = localStorage.getItem(storageKey);
    const reports: BugReport[] = existing ? JSON.parse(existing) : [];
    
    reports.push(report);
    
    // Limite à 100 rapports max en local (purge les plus vieux)
    if (reports.length > 100) {
      reports.splice(0, reports.length - 100);
    }
    
    localStorage.setItem(storageKey, JSON.stringify(reports));
  } catch (error) {
    console.error('[BugReport] Erreur localStorage:', error);
  }
}

/**
 * Envoie vers Redis Upstash
 * ✅ v2.0 : Structure optimisée par catégorie
 */
async function sendBugReportToRedis(report: BugReport): Promise<void> {
  try {
    const questionId = report.questionId;
    
    // ✅ 1. LISTES PAR CATÉGORIE (pour traiter section par section)
    for (const category of report.categories) {
      await fetch(`${REDIS_URL}/lpush/bug:${category}/${questionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${REDIS_TOKEN}`
        }
      });
      
      // Compteur par catégorie
      await fetch(`${REDIS_URL}/hincrby/bug_stats:by_category/${category}/1`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${REDIS_TOKEN}`
        }
      });
    }
    
    // ✅ 2. DÉTAILS COMPLETS PAR QUESTION
    await fetch(`${REDIS_URL}/set/bug_details:${questionId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(report)
    });
    
    // ✅ 3. COMPTEUR PAR QUESTION (sorted set pour ranking)
    await fetch(`${REDIS_URL}/zincrby/bug_stats:by_question/1/${questionId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });
    
    // ✅ 4. LISTE GLOBALE (backup)
    await fetch(`${REDIS_URL}/lpush/bug_reports:all`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(report)
    });
    
    // 5. Expiration 90 jours sur les détails
    await fetch(`${REDIS_URL}/expire/bug_details:${questionId}/7776000`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });
    
    console.info('[BugReport] ✅ Envoyé vers Redis - Catégories:', report.categories.join(', '));
  } catch (error) {
    console.warn('[BugReport] Erreur Redis (ignorée):', error);
  }
}

/**
 * Récupère les rapports locaux
 */
export function getLocalBugReports(): BugReport[] {
  try {
    const storageKey = 'iade_bug_reports_v1';
    const data = localStorage.getItem(storageKey);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('[BugReport] Erreur lecture localStorage:', error);
    return [];
  }
}

/**
 * Récupère les stats des bugs depuis Redis
 */
export async function getBugReportStats(): Promise<BugReportStats | null> {
  if (!REDIS_ENABLED) {
    return null;
  }
  
  try {
    // Récupère les stats par catégorie
    const categoriesResponse = await fetch(`${REDIS_URL}/hgetall/bug_stats:categories`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`
      }
    });
    
    if (!categoriesResponse.ok) {
      return null;
    }
    
    const data = await categoriesResponse.json();
    const byCategory = data.result || {};
    
    // Calcule le total
    const totalReports = Object.values(byCategory).reduce((sum: number, count) => sum + (count as number), 0);
    
    return {
      totalReports,
      byCategory,
      bySeverity: { low: 0, medium: 0, high: 0 }, // À implémenter si nécessaire
      byStatus: { pending: 0, reviewed: 0, fixed: 0, rejected: 0 },
      mostReportedQuestions: []
    };
  } catch (error) {
    console.error('[BugReport] Erreur stats Redis:', error);
    return null;
  }
}

/**
 * Récupère les bugs d'une question spécifique
 */
export async function getBugReportsForQuestion(questionId: string): Promise<BugReport[]> {
  if (!REDIS_ENABLED) {
    // Fallback sur localStorage
    const localReports = getLocalBugReports();
    return localReports.filter(r => r.questionId === questionId);
  }
  
  try {
    const response = await fetch(
      `${REDIS_URL}/lrange/bug_reports:question:${questionId}/0/-1`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${REDIS_TOKEN}`
        }
      }
    );
    
    if (!response.ok) {
      return [];
    }
    
    const data = await response.json();
    return data.result || [];
  } catch (error) {
    console.error('[BugReport] Erreur lecture Redis:', error);
    return [];
  }
}

// =============================================================================
// EXPORT
// =============================================================================

export default {
  submitBugReport,
  getLocalBugReports,
  getBugReportStats,
  getBugReportsForQuestion
};

