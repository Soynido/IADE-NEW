/**
 * Types pour le système de rapport de bugs structuré
 * Permet aux utilisateurs de remonter des problèmes spécifiques
 * Format exploitable par l'IA pour corrections automatiques
 */

export type BugCategory = 
  | 'question_ambigue'           // Question mal formulée ou ambiguë
  | 'reponse_incorrecte'         // Mauvaise réponse marquée comme correcte
  | 'plusieurs_reponses'         // Plusieurs réponses possibles
  | 'explication_manquante'      // Explication absente ou incomplète
  | 'explication_incorrecte'     // Explication fausse ou confuse
  | 'reference_incorrecte'       // Lien vers cours pointant vers mauvaise page
  | 'faute_orthographe'          // Faute d'orthographe ou grammaire
  | 'terme_medical_incorrect'    // Terme biomédical erroné
  | 'options_repetees'           // Options en double ou trop similaires
  | 'difficulte_mal_calibree'    // Difficulté (easy/medium/hard) inadaptée
  | 'hors_programme'             // Question hors du programme IADE
  | 'autre';                     // Autre problème

export interface BugReport {
  // Identification
  bugId: string;                 // ID unique du bug
  questionId: string;            // ID de la question concernée
  userId?: string;               // ID anonyme de l'utilisateur (optionnel)
  
  // Classification
  category: BugCategory;         // Type de bug
  severity: 'low' | 'medium' | 'high'; // Gravité
  
  // Description
  description: string;           // Description libre du problème
  suggestedFix?: string;         // Suggestion de correction (optionnel)
  
  // Contexte
  userAnswer?: number;           // Réponse choisie par l'utilisateur
  expectedAnswer?: number;       // Réponse attendue selon l'utilisateur
  context: {
    mode: 'revision' | 'entrainement' | 'concours'; // Mode d'utilisation
    moduleId: string;            // Module concerné
    timestamp: string;           // Quand le bug a été rencontré
    deviceInfo?: string;         // Info device (mobile/desktop)
  };
  
  // Métadonnées
  status: 'pending' | 'reviewed' | 'fixed' | 'rejected'; // Statut du traitement
  aiAnalysis?: {
    confidence: number;          // Confiance de l'IA (0-1)
    suggestedCategory?: BugCategory; // Catégorie suggérée par l'IA
    autoFixable: boolean;        // Peut être corrigé automatiquement
    proposedCorrection?: string; // Correction proposée par l'IA
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
  category: BugCategory;
  description: string;
  suggestedFix?: string;
  expectedAnswer?: number;
}

