/**
 * Types globaux IADE NEW
 * Conformes aux schémas spec.md Section III
 */

export interface Question {
  id: string;
  module_id: string;
  text: string;
  options: string[]; // Exactement 4
  correctAnswer: number; // 0-3
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  mode: 'revision' | 'entrainement' | 'concours';
  source_pdf: string;
  page: number;
  chunk_id: string;
  source_context: string;
  
  // Scores de validation
  biomedical_score: number;
  biomedical_threshold: number;
  context_score: number;
  keywords_overlap: number;
  stylistic_distance?: number;
  explanation_length?: number;
  
  flags?: {
    ambiguous?: boolean;
    calc_needed?: boolean;
    validated_by_expert?: boolean;
  };
}

export interface Exam {
  exam_id: string;
  title: string;
  description: string;
  duration_minutes: number;
  question_count: number;
  question_ids: string[];
  module_weights: Record<string, number>;
  difficulty_distribution: {
    easy: number;
    medium: number;
    hard: number;
  };
  questions: Question[];
}

export interface Module {
  module_id: string;
  title: string;
  keywords: string[];
  sections: Section[];
  coverage_percent?: number;
  question_count?: number;
  biomedical_threshold?: number;
}

export interface Section {
  section_id: string;
  title: string;
  pages: number[];
  module_id: string;
  chunks: Chunk[];
}

export interface Chunk {
  chunk_id: string;
  text: string;
  source_pdf: string;
  page_start: number;
  page_end: number;
  token_count: number;
}

