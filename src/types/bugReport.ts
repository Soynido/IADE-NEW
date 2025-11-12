/**
 * Types pour le système de rapport de bugs structuré
 * v2.0 : Support multi-catégories + Redis par catégorie
 */

export type BugCategory = 
  | 'question_ambigue'
  | 'reponse_incorrecte'
  | 'plusieurs_reponses'
  | 'explication_manquante'
  | 'explication_incorrecte'
  | 'reference_incorrecte'
  | 'faute_orthographe'
  | 'terme_medical_incorrect'
  | 'options_repetees'
  | 'difficulte_mal_calibree'
  | 'hors_programme'
  | 'autre';

export interface BugReport {
  bugId: string;
  questionId: string;
  userId?: string;
  
  // ✅ v2.0 : MULTI-CATÉGORIES
  categories: BugCategory[];  // Plusieurs catégories possibles
  severity: 'low' | 'medium' | 'high';
  
  // ✅ v2.0 : UN SEUL CHAMP GLOBAL
  description: string;  // Couvre toutes les catégories
  suggestedFix?: string;
  
  userAnswer?: number;
  expectedAnswer?: number;
  
  context: {
    mode: 'revision' | 'entrainement' | 'concours';
    moduleId: string;
    timestamp: string;
    deviceInfo?: string;
  };
  
  status: 'pending' | 'reviewed' | 'fixed' | 'rejected';
  aiAnalysis?: {
    confidence: number;
    suggestedCategory?: BugCategory;
    autoFixable: boolean;
    proposedCorrection?: string;
  };
  
  createdAt: string;
  updatedAt?: string;
}

export interface BugReportStats {
  totalReports: number;
  byCategory: Record<BugCategory, number>;
  bySeverity: Record<'low' | 'medium' | 'high', number>;
  byStatus: Record<BugReport['status'], number>;
  mostReportedQuestions: Array<{
    questionId: string;
    count: number;
    categories: BugCategory[];
  }>;
}

export interface BugReportFormData {
  categories: BugCategory[];  // ✅ Plusieurs catégories
  description: string;
  suggestedFix?: string;
  expectedAnswer?: number;
}
