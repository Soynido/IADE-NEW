/**
 * Composant RevisionMode - Mode Révision
 * Tâche [042] - Phase 6 : Frontend Core
 * 
 * Features:
 * - Liste filtrable par module
 * - Intégration QuestionCard
 * - Explication immédiate après réponse
 * - Bouton "Voir le cours"
 * - Marquage "À revoir"
 * - Pagination
 */

import { useState, useEffect } from 'react';
import { QuestionCard } from './QuestionCard';
import { useUserStore } from '@/store/useUserStore';
import { Question } from '@/types';

export function RevisionMode() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [filteredQuestions, setFilteredQuestions] = useState<Question[]>([]);
  const [selectedModule, setSelectedModule] = useState<string>('all');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [toReview, setToReview] = useState<Set<string>>(new Set());
  
  const { incrementAttempt, addFeedback } = useUserStore();

  // Chargement des questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const response = await fetch('/src/data/questions/revision.json');
        const data = await response.json();
        setQuestions(data);
        setFilteredQuestions(data);
        setLoading(false);
      } catch (error) {
        console.error('Erreur chargement questions:', error);
        setLoading(false);
      }
    };
    
    loadQuestions();
  }, []);

  // Filtrage par module
  useEffect(() => {
    if (selectedModule === 'all') {
      setFilteredQuestions(questions);
    } else {
      const filtered = questions.filter(q => q.module_id === selectedModule);
      setFilteredQuestions(filtered);
    }
    setCurrentIndex(0); // Reset à la première question
  }, [selectedModule, questions]);

  // Récupération modules uniques
  const modules = Array.from(new Set(questions.map(q => q.module_id))).sort();

  const handleAnswer = (questionId: string, selectedAnswer: number, isCorrect: boolean) => {
    const currentQuestion = filteredQuestions[currentIndex];
    if (currentQuestion) {
      incrementAttempt(
        currentQuestion.module_id,
        questionId,
        isCorrect,
        isCorrect ? [] : extractKeywords(currentQuestion.text)
      );
    }
  };

  const handleFeedback = (questionId: string, score: 1 | 2 | 3) => {
    addFeedback(questionId, score);
  };

  const handleViewCourse = (sourcePdf?: string, page?: number) => {
    if (!sourcePdf || !page) return;
    
    // Nettoie le nom du PDF
    const pdfName = sourcePdf.replace('.pdf', '');
    const pdfUrl = `/pdfs/${pdfName}.pdf#page=${page}`;
    
    // Ouvre dans un nouvel onglet
    window.open(pdfUrl, '_blank');
  };

  const handleMarkToReview = () => {
    const currentQuestion = filteredQuestions[currentIndex];
    if (currentQuestion) {
      const questionId = currentQuestion.id || currentQuestion.chunk_id;
      const newToReview = new Set(toReview);
      
      if (toReview.has(questionId)) {
        newToReview.delete(questionId);
      } else {
        newToReview.add(questionId);
      }
      
      setToReview(newToReview);
      
      // Persistance dans localStorage
      localStorage.setItem('iade_to_review', JSON.stringify(Array.from(newToReview)));
    }
  };

  const handleNext = () => {
    if (currentIndex < filteredQuestions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const extractKeywords = (text: string): string[] => {
    // Extraction simple de mots-clés (améliorer avec NLP si besoin)
    const words = text.toLowerCase().split(/\s+/);
    return words.filter(w => w.length > 5).slice(0, 3);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des questions...</p>
        </div>
      </div>
    );
  }

  if (filteredQuestions.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
          <p className="text-yellow-800">
            Aucune question disponible pour le module sélectionné.
          </p>
        </div>
      </div>
    );
  }

  const currentQuestion = filteredQuestions[currentIndex];
  const isMarkedToReview = toReview.has(currentQuestion.id || currentQuestion.chunk_id);

  return (
    <div className="container mx-auto px-3 md:px-4 py-4 md:py-8 max-w-4xl pb-20 md:pb-8">
      {/* En-tête */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Mode Révision</h1>
        <p className="text-sm md:text-base text-gray-600">
          Apprenez à votre rythme avec des explications immédiates
        </p>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-lg shadow p-3 md:p-4 mb-4 md:mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 md:gap-0">
          <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 w-full md:w-auto">
            <label className="text-sm font-medium text-gray-700">Module :</label>
          <select
            value={selectedModule}
            onChange={(e) => setSelectedModule(e.target.value)}
            className="px-3 md:px-4 py-2 text-sm md:text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-gray-900 w-full md:w-auto"
          >
              <option value="all">Tous les modules ({questions.length})</option>
              {modules.map(module => (
                <option key={module} value={module}>
                  {module.replace('_', ' ').toUpperCase()} (
                    {questions.filter(q => q.module_id === module).length}
                  )
                </option>
              ))}
            </select>
          </div>
          
          <div className="text-sm text-gray-600">
            Question {currentIndex + 1} / {filteredQuestions.length}
          </div>
        </div>
      </div>

      {/* Question Card */}
      <QuestionCard
        question={currentQuestion}
        showExplanation={true}
        showFeedback={true}
        onAnswer={handleAnswer}
        onFeedback={handleFeedback}
        onViewCourse={handleViewCourse}
      />

      {/* Navigation */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2 md:gap-0 mt-4 md:mt-6">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="px-4 md:px-6 py-3 bg-gray-200 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 transition touch-manipulation text-sm md:text-base"
        >
          ← Précédente
        </button>
        
        <button
          onClick={handleMarkToReview}
          className={`px-4 md:px-6 py-3 rounded-lg transition touch-manipulation text-sm md:text-base ${
            isMarkedToReview
              ? 'bg-yellow-500 text-white hover:bg-yellow-600'
              : 'bg-white border-2 border-yellow-500 text-yellow-700 hover:bg-yellow-50'
          }`}
        >
          {isMarkedToReview ? '✓ À revoir' : '⭐ Marquer'}
        </button>
        
        <button
          onClick={handleNext}
          disabled={currentIndex === filteredQuestions.length - 1}
          className="px-4 md:px-6 py-3 bg-primary-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-700 transition touch-manipulation text-sm md:text-base"
        >
          Suivante →
        </button>
      </div>

      {/* Progression */}
      <div className="mt-4 md:mt-6">
        <div className="flex justify-between text-xs md:text-sm text-gray-600 mb-2">
          <span>Question {currentIndex + 1} / {filteredQuestions.length}</span>
          <span>{Math.round(((currentIndex + 1) / filteredQuestions.length) * 100)}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-600 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / filteredQuestions.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}

