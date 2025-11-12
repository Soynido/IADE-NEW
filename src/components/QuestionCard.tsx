/**
 * Composant QuestionCard - Affichage d'une question QCM
 * Tâche [041] - Phase 6 : Frontend Core
 * 
 * Features:
 * - Affichage question + 4 options
 * - Sélection réponse (boutons radio)
 * - Feedback visuel (vert/rouge) après réponse
 * - Explication conditionnelle
 * - Bouton "Voir le cours"
 * - Système de notation Bad/Good/Very Good
 */

import { useState, useEffect } from 'react';
import { Question } from '@/types';
import { BugReportModal } from './BugReportModal';
import { submitBugReport } from '@/utils/bugReportApi';
import { BugReportFormData } from '@/types/bugReport';

interface QuestionCardProps {
  question: Question;
  showExplanation?: boolean; // Affiche explication immédiatement ou après réponse
  showFeedback?: boolean; // Active système Bad/Good/Very Good
  onAnswer?: (questionId: string, selectedAnswer: number, isCorrect: boolean) => void;
  onFeedback?: (questionId: string, score: 1 | 2 | 3) => void;
  onViewCourse?: (sourcePdf: string, page: number) => void;
}

export function QuestionCard({
  question,
  showExplanation = false,
  showFeedback = false,
  onAnswer,
  onFeedback,
  onViewCourse
}: QuestionCardProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [hasAnswered, setHasAnswered] = useState(false);
  const [showBugReportModal, setShowBugReportModal] = useState(false);

  // Reset l'état quand la question change
  useEffect(() => {
    setSelectedAnswer(null);
    setHasAnswered(false);
  }, [question.id, question.chunk_id, question.text]);

  const handleSelectOption = (optionIndex: number) => {
    if (hasAnswered && !showExplanation) return; // Bloqué après réponse en mode examen
    
    setSelectedAnswer(optionIndex);
    
    if (!hasAnswered) {
      setHasAnswered(true);
      const isCorrect = optionIndex === question.correctAnswer;
      
      if (onAnswer) {
        onAnswer(question.id || question.chunk_id, optionIndex, isCorrect);
      }
    }
  };

  const handleFeedback = (score: 1 | 2 | 3) => {
    if (onFeedback) {
      onFeedback(question.id || question.chunk_id, score);
    }
  };

  const handleBugReport = async (reportData: BugReportFormData) => {
    try {
      await submitBugReport(
        reportData,
        question,
        'revision', // TODO: passer le mode réel depuis props
        selectedAnswer ?? undefined
      );
    } catch (error) {
      console.error('Erreur soumission bug report:', error);
      throw error;
    }
  };

  const getOptionClass = (index: number): string => {
    const baseClass = "w-full text-left px-4 py-3 border-2 rounded-lg transition-all duration-200 ";
    
    // Pas encore répondu
    if (!hasAnswered) {
      return baseClass + "border-gray-300 hover:border-primary-400 hover:bg-primary-50";
    }
    
    // Après réponse
    const isCorrect = index === question.correctAnswer;
    const isSelected = index === selectedAnswer;
    
    if (isCorrect) {
      return baseClass + "border-green-500 bg-green-50 text-green-900";
    }
    
    if (isSelected && !isCorrect) {
      return baseClass + "border-red-500 bg-red-50 text-red-900";
    }
    
    return baseClass + "border-gray-200 bg-gray-50 opacity-60";
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      {/* En-tête */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-primary-100 text-primary-700">
            {(question.module_id || 'module').replace('_', ' ').toUpperCase()}
          </span>
          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
            question.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
            question.difficulty === 'hard' ? 'bg-red-100 text-red-700' :
            'bg-yellow-100 text-yellow-700'
          }`}>
            {(question.difficulty || 'medium').toUpperCase()}
          </span>
        </div>
        
        {question.source_pdf && (
          <button
            onClick={() => onViewCourse?.(question.source_pdf, question.page_number || question.page || 1)}
            className="text-sm text-primary-600 hover:text-primary-800 flex items-center gap-1"
          >
            📖 Voir le cours (p. {question.page_number || question.page || 1})
          </button>
        )}
      </div>

      {/* Question */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {question.text}
      </h3>

      {/* Options */}
      <div className="space-y-2 mb-4">
        {question.options.map((option, index) => (
          <button
            key={index}
            onClick={() => handleSelectOption(index)}
            disabled={hasAnswered && !showExplanation}
            className={getOptionClass(index)}
          >
            <div className="flex items-center gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center font-semibold text-sm">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="flex-1">{option}</span>
              {hasAnswered && index === question.correctAnswer && (
                <span className="flex-shrink-0 text-green-600 font-bold">✓</span>
              )}
              {hasAnswered && index === selectedAnswer && index !== question.correctAnswer && (
                <span className="flex-shrink-0 text-red-600 font-bold">✗</span>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Explication (conditionnelle) */}
      {(hasAnswered || showExplanation) && (
        <div className="mt-4 md:mt-6 p-3 md:p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <h4 className="text-sm md:text-base font-semibold text-blue-900 mb-2">💡 Explication</h4>
          <p className="text-sm md:text-base text-gray-700 leading-relaxed">
            {question.explanation}
          </p>
          
          {question.source_context && (
            <div className="mt-3 pt-3 border-t border-blue-200">
              <p className="text-sm text-gray-600 italic">
                <strong>Source:</strong> {question.source_context.substring(0, 200)}
                {question.source_context.length > 200 && '...'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Système de feedback (Bad/Good/Very Good) */}
      {hasAnswered && showFeedback && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2">Cette question vous a-t-elle été utile ?</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleFeedback(1)}
              className="px-4 py-2 text-sm rounded-lg border-2 border-red-300 text-red-700 hover:bg-red-50 transition"
            >
              😞 Pas utile
            </button>
            <button
              onClick={() => handleFeedback(2)}
              className="px-4 py-2 text-sm rounded-lg border-2 border-yellow-300 text-yellow-700 hover:bg-yellow-50 transition"
            >
              😐 Utile
            </button>
            <button
              onClick={() => handleFeedback(3)}
              className="px-4 py-2 text-sm rounded-lg border-2 border-green-300 text-green-700 hover:bg-green-50 transition"
            >
              😊 Très utile
            </button>
            
            {/* Bouton rapport de bug */}
            <button
              onClick={() => setShowBugReportModal(true)}
              className="ml-auto px-4 py-2 text-sm rounded-lg border-2 border-orange-300 text-orange-700 hover:bg-orange-50 transition font-medium"
              title="Signaler un problème avec cette question"
            >
              🐛 Signaler un bug
            </button>
          </div>
        </div>
      )}

      {/* Modal de rapport de bug */}
      <BugReportModal
        question={question}
        mode="revision" // TODO: passer le mode réel depuis props
        userAnswer={selectedAnswer ?? undefined}
        isOpen={showBugReportModal}
        onClose={() => setShowBugReportModal(false)}
        onSubmit={handleBugReport}
      />
    </div>
  );
}

