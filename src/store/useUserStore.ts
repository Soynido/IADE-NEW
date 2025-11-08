/**
 * Store Zustand - Gestion état utilisateur
 * Tâche [040] - Phase 6 : Frontend Core
 * 
 * Fonctionnalités:
 * - Stats utilisateur (attempts, correct, par module)
 * - Historique feedback (Bad/Good/Very Good)
 * - Résultats examens blancs
 * - Persistance localStorage
 * - Purge automatique logs > 90 jours
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// =============================================================================
// TYPES
// =============================================================================

export interface ModuleStats {
  attempts: number;
  correct: number;
  lastSeen: string; // ISO date
  weakKeywords: string[]; // Mots-clés des questions ratées
}

export interface FeedbackLog {
  questionId: string;
  score: 1 | 2 | 3; // Bad / Good / Very Good
  ts: string; // ISO timestamp
}

export interface ExamResult {
  examId: string;
  score: number;
  totalQuestions: number;
  date: string;
  duration: number; // minutes
}

export interface UserStats {
  attempts: number;
  correct: number;
  byModule: Record<string, ModuleStats>;
  streakDays: number;
  lastActivityDate: string;
  feedbackLog: FeedbackLog[];
  examResults: ExamResult[];
  nextReview: Record<string, string>; // questionId → ISO date (SM-2)
}

interface UserStore {
  stats: UserStats;
  
  // Actions
  incrementAttempt: (moduleId: string, questionId: string, correct: boolean, weakKeywords?: string[]) => void;
  addFeedback: (questionId: string, score: 1 | 2 | 3) => void;
  addExamResult: (examId: string, score: number, totalQuestions: number, duration: number) => void;
  
  // Getters
  getWeakModules: () => Array<{ moduleId: string; score: number }>;
  getStreakDays: () => number;
  
  // Maintenance
  purgeOldLogs: () => void;
  resetStats: () => void;
}

// =============================================================================
// ÉTAT INITIAL
// =============================================================================

const initialStats: UserStats = {
  attempts: 0,
  correct: 0,
  byModule: {},
  streakDays: 0,
  lastActivityDate: new Date().toISOString(),
  feedbackLog: [],
  examResults: [],
  nextReview: {}
};

// =============================================================================
// UTILITAIRES
// =============================================================================

/**
 * Purge les logs > 90 jours (sauf examResults conservés indéfiniment)
 */
function purgeOldLogs(stats: UserStats): UserStats {
  const cutoffDate = Date.now() - 90 * 24 * 60 * 60 * 1000; // 90 jours
  
  return {
    ...stats,
    feedbackLog: stats.feedbackLog.filter(log => 
      new Date(log.ts).getTime() > cutoffDate
    ),
    // Conserve examResults indéfiniment
    // Purge byModule si lastSeen > 1 an
    byModule: Object.fromEntries(
      Object.entries(stats.byModule).filter(([_, data]) => 
        new Date(data.lastSeen).getTime() > Date.now() - 365 * 24 * 60 * 60 * 1000
      )
    )
  };
}

/**
 * Calcule le nombre de jours actifs (jours avec ≥ 1 session)
 */
function calculateStreakDays(stats: UserStats): number {
  const today = new Date().toISOString().split('T')[0];
  const lastActivity = stats.lastActivityDate.split('T')[0];
  
  if (lastActivity === today) {
    return stats.streakDays;
  } else {
    // Nouvelle journée
    const lastDate = new Date(lastActivity);
    const todayDate = new Date(today);
    const diffDays = Math.floor((todayDate.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      // Jour consécutif
      return stats.streakDays + 1;
    } else {
      // Reset streak
      return 1;
    }
  }
}

/**
 * Met à jour la date d'activité et le streak
 */
function updateActivity(stats: UserStats): UserStats {
  const today = new Date().toISOString();
  const streakDays = calculateStreakDays(stats);
  
  return {
    ...stats,
    lastActivityDate: today,
    streakDays
  };
}

// =============================================================================
// STORE
// =============================================================================

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      stats: initialStats,
      
      // ========== ACTIONS ==========
      
      incrementAttempt: (moduleId, questionId, correct, weakKeywords = []) => {
        set((state) => {
          const newStats = updateActivity(state.stats);
          
          // Mise à jour globale
          newStats.attempts += 1;
          if (correct) {
            newStats.correct += 1;
          }
          
          // Mise à jour par module
          if (!newStats.byModule[moduleId]) {
            newStats.byModule[moduleId] = {
              attempts: 0,
              correct: 0,
              lastSeen: new Date().toISOString(),
              weakKeywords: []
            };
          }
          
          newStats.byModule[moduleId].attempts += 1;
          if (correct) {
            newStats.byModule[moduleId].correct += 1;
          } else {
            // Ajoute weak keywords si incorrect
            if (weakKeywords.length > 0) {
              const currentWeak = newStats.byModule[moduleId].weakKeywords;
              const combined = [...new Set([...currentWeak, ...weakKeywords])];
              newStats.byModule[moduleId].weakKeywords = combined.slice(0, 10); // Top 10
            }
          }
          newStats.byModule[moduleId].lastSeen = new Date().toISOString();
          
          return { stats: newStats };
        });
      },
      
      addFeedback: (questionId, score) => {
        set((state) => {
          const newStats = { ...state.stats };
          
          newStats.feedbackLog.push({
            questionId,
            score,
            ts: new Date().toISOString()
          });
          
          return { stats: newStats };
        });
      },
      
      addExamResult: (examId, score, totalQuestions, duration) => {
        set((state) => {
          const newStats = updateActivity(state.stats);
          
          newStats.examResults.push({
            examId,
            score,
            totalQuestions,
            date: new Date().toISOString(),
            duration
          });
          
          return { stats: newStats };
        });
      },
      
      // ========== GETTERS ==========
      
      getWeakModules: () => {
        const { stats } = get();
        
        return Object.entries(stats.byModule)
          .map(([moduleId, data]) => ({
            moduleId,
            score: data.attempts > 0 ? data.correct / data.attempts : 0
          }))
          .sort((a, b) => a.score - b.score) // Tri par score croissant
          .slice(0, 5); // Top 5 modules faibles
      },
      
      getStreakDays: () => {
        const { stats } = get();
        return stats.streakDays;
      },
      
      // ========== MAINTENANCE ==========
      
      purgeOldLogs: () => {
        set((state) => ({
          stats: purgeOldLogs(state.stats)
        }));
      },
      
      resetStats: () => {
        set({ stats: initialStats });
      }
    }),
    {
      name: 'iade_user_stats_v1',
      version: 1,
      // Purge automatique au chargement
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.purgeOldLogs();
        }
      }
    }
  )
);

