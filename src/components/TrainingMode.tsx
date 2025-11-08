/**
 * Composant TrainingMode - Mode Entraînement Adaptatif
 * Tâche [043] - Phase 6 : Frontend Core
 * 
 * Features:
 * - Sélection module
 * - Session 10 questions adaptatives
 * - Score en temps réel
 * - Feedback immédiat
 * - Progression niveau (easy → medium → hard)
 */

import { useState, useEffect } from 'react';
import { QuestionCard } from './QuestionCard';
import { useUserStore } from '@/store/useUserStore';
import { Question } from '@/types';

const QUESTIONS_PER_SESSION = 10;

export function TrainingMode() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [sessionQuestions, setSessionQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);
  const [score, setScore] = useState(0);
  const [currentDifficulty, setCurrentDifficulty] = useState<'easy' | 'medium' | 'hard'>('easy');
  const [loading, setLoading] = useState(true);
  
  const { incrementAttempt, addFeedback } = useUserStore();

  // Chargement questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const response = await fetch('/data/questions/entrainement.json');
        const data = await response.json();
        setQuestions(data);
        setLoading(false);
      } catch (error) {
        console.error('Erreur chargement questions:', error);
        setLoading(false);
      }
    };
    
    loadQuestions();
  }, []);

  const modules = Array.from(new Set(questions.map(q => q.module_id))).sort();

  const startSession = () => {
    if (!selectedModule) return;
    
    // Filtre questions du module
    const moduleQuestions = questions.filter(q => q.module_id === selectedModule);
    
    // Sélection adaptative (commence easy)
    const selected = selectAdaptiveQuestions(moduleQuestions, 'easy', QUESTIONS_PER_SESSION);
    
    setSessionQuestions(selected);
    setCurrentIndex(0);
    setScore(0);
    setCurrentDifficulty('easy');
    setSessionActive(true);
  };

  const selectAdaptiveQuestions = (
    pool: Question[],
    difficulty: 'easy' | 'medium' | 'hard',
    count: number
  ): Question[] => {
    // Filtre par difficulté
    let difficultyQuestions = pool.filter(q => q.difficulty === difficulty);
    
    // Si pas assez, prend difficulté adjacente
    if (difficultyQuestions.length < count) {
      const allDifficulties = pool;
      difficultyQuestions = allDifficulties;
    }
    
    // Shuffle et prend N questions
    const shuffled = [...difficultyQuestions].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  };

  const adjustDifficulty = (correctCount: number, totalAnswered: number) => {
    const successRate = correctCount / totalAnswered;
    
    // Adaptation niveau
    if (successRate > 0.7 && currentDifficulty !== 'hard') {
      // Augmente niveau
      if (currentDifficulty === 'easy') {
        setCurrentDifficulty('medium');
      } else if (currentDifficulty === 'medium') {
        setCurrentDifficulty('hard');
      }
    } else if (successRate < 0.4 && currentDifficulty !== 'easy') {
      // Diminue niveau
      if (currentDifficulty === 'hard') {
        setCurrentDifficulty('medium');
      } else if (currentDifficulty === 'medium') {
        setCurrentDifficulty('easy');
      }
    }
  };

  const handleAnswer = (questionId: string, selectedAnswer: number, isCorrect: boolean) => {
    const currentQuestion = sessionQuestions[currentIndex];
    
    if (currentQuestion) {
      incrementAttempt(
        currentQuestion.module_id,
        questionId,
        isCorrect,
        isCorrect ? [] : extractKeywords(currentQuestion.text)
      );
      
      if (isCorrect) {
        setScore(score + 1);
      }
      
      // Ajuste difficulté après quelques questions
      if (currentIndex >= 2) {
        adjustDifficulty(score + (isCorrect ? 1 : 0), currentIndex + 1);
      }
    }
  };

  const handleNext = () => {
    if (currentIndex < sessionQuestions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      endSession();
    }
  };

  const endSession = () => {
    setSessionActive(false);
  };

  const extractKeywords = (text: string): string[] => {
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

  // Écran de sélection module
  if (!sessionActive) {
    const finalScore = sessionQuestions.length > 0 ? score : null;
    
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mode Entraînement</h1>
        <p className="text-gray-600 mb-8">
          Session de 10 questions adaptatives avec feedback immédiat
        </p>

        {/* Résultat session précédente */}
        {finalScore !== null && (
          <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-lg mb-8">
            <h3 className="text-xl font-semibold text-green-900 mb-2">Session terminée !</h3>
            <p className="text-3xl font-bold text-green-700">
              {finalScore} / {sessionQuestions.length} ({(finalScore / sessionQuestions.length * 100).toFixed(0)}%)
            </p>
          </div>
        )}

        {/* Sélection module */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Choisissez un module</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {modules.map(module => {
              const moduleQuestionsCount = questions.filter(q => q.module_id === module).length;
              
              return (
                <button
                  key={module}
                  onClick={() => setSelectedModule(module)}
                  className={`p-4 rounded-lg border-2 transition text-left ${
                    selectedModule === module
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {module.replace('_', ' ').toUpperCase()}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {moduleQuestionsCount} questions disponibles
                  </p>
                </button>
              );
            })}
          </div>

          <button
            onClick={startSession}
            disabled={!selectedModule}
            className="mt-6 w-full px-6 py-3 bg-primary-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-700 transition text-lg font-semibold"
          >
            Démarrer la session ({QUESTIONS_PER_SESSION} questions)
          </button>
        </div>
      </div>
    );
  }

  // Session en cours
  const currentQuestion = sessionQuestions[currentIndex];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* En-tête session */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Session : {selectedModule?.replace('_', ' ').toUpperCase()}
            </h2>
            <p className="text-sm text-gray-600">
              Question {currentIndex + 1} / {sessionQuestions.length} • Niveau: {currentDifficulty.toUpperCase()}
            </p>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold text-primary-600">
              {score} / {currentIndex}
            </div>
            <div className="text-sm text-gray-600">
              {currentIndex > 0 ? ((score / currentIndex) * 100).toFixed(0) : 0}% réussite
            </div>
          </div>
        </div>
      </div>

      {/* Question */}
      <QuestionCard
        question={currentQuestion}
        showExplanation={true}
        showFeedback={true}
        onAnswer={handleAnswer}
        onFeedback={addFeedback}
        onViewCourse={handleViewCourse}
      />

      {/* Navigation */}
      <div className="flex justify-end mt-6">
        <button
          onClick={handleNext}
          className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition text-lg font-semibold"
        >
          {currentIndex === sessionQuestions.length - 1 ? 'Terminer la session' : 'Question suivante →'}
        </button>
      </div>

      {/* Progression */}
      <div className="mt-6">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-600 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / sessionQuestions.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}

