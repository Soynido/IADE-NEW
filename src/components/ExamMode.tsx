/**
 * Composant ExamMode - Mode Concours Blanc
 * Tâche [050] - Phase 7 : Modes Avancés
 * 
 * Features:
 * - Chronomètre 120 minutes
 * - Navigation libre entre 60 questions
 * - Blocage explications pendant l'épreuve
 * - Correction à la fin uniquement
 * - Tableau récapitulatif avec temps moyen/Q
 */

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { QuestionCard } from './QuestionCard';
import { useUserStore } from '@/store/useUserStore';
import { Exam, Question } from '@/types';

const EXAM_DURATION_MINUTES = 120;

export function ExamMode() {
  const { examId } = useParams<{ examId: string }>();
  const [exam, setExam] = useState<Exam | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(EXAM_DURATION_MINUTES * 60); // en secondes
  const [examStarted, setExamStarted] = useState(false);
  const [examFinished, setExamFinished] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const { addExamResult } = useUserStore();

  // Chargement examen
  useEffect(() => {
    const loadExam = async () => {
      if (!examId) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await fetch(`/data/exams/${examId}.json`);
        const data: Exam = await response.json();
        setExam(data);
        setLoading(false);
      } catch (error) {
        console.error('Erreur chargement examen:', error);
        setLoading(false);
      }
    };
    
    loadExam();
  }, [examId]);

  // Chronomètre
  useEffect(() => {
    if (examStarted && !examFinished) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }
  }, [examStarted, examFinished]);

  const startExam = () => {
    setExamStarted(true);
    setTimeRemaining(EXAM_DURATION_MINUTES * 60);
  };

  const handleSelectAnswer = (questionIndex: number, answer: number) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer
    });
  };

  const handleNavigate = (index: number) => {
    setCurrentQuestionIndex(index);
  };

  const handleSubmit = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setExamFinished(true);
    
    // Calcul score
    if (exam) {
      const correct = exam.questions.reduce((count, question, index) => {
        return count + (selectedAnswers[index] === question.correctAnswer ? 1 : 0);
      }, 0);
      
      const duration = EXAM_DURATION_MINUTES - Math.floor(timeRemaining / 60);
      
      // Sauvegarde résultat
      addExamResult(
        exam.exam_id,
        (correct / exam.questions.length) * 100,
        exam.questions.length,
        duration
      );
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <p className="text-red-800">Examen introuvable</p>
        </div>
      </div>
    );
  }

  // Écran de démarrage
  if (!examStarted) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{exam.title}</h1>
          <p className="text-gray-600 mb-8">{exam.description}</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded mb-8">
            <h3 className="font-semibold text-blue-900 mb-4">Règles de l'examen</h3>
            <ul className="space-y-2 text-blue-800">
              <li>✓ {exam.question_count} questions</li>
              <li>✓ Durée : {exam.duration_minutes} minutes</li>
              <li>✓ Navigation libre (retour en arrière autorisé)</li>
              <li>⚠️ Pas d'explication pendant l'épreuve</li>
              <li>✓ Correction complète à la fin</li>
            </ul>
          </div>
          
          <button
            onClick={startExam}
            className="w-full px-6 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition text-xl font-semibold"
          >
            Démarrer l'examen
          </button>
        </div>
      </div>
    );
  }

  // Écran de correction (après soumission)
  if (examFinished) {
    const score = exam.questions.reduce((count, question, index) => {
      return count + (selectedAnswers[index] === question.correctAnswer ? 1 : 0);
    }, 0);
    
    const percent = (score / exam.questions.length) * 100;
    const avgTimePerQuestion = (EXAM_DURATION_MINUTES - Math.floor(timeRemaining / 60)) / exam.questions.length;
    
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Résultats - {exam.title}</h1>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-4xl font-bold text-blue-600">{score}/{exam.questions.length}</div>
              <div className="text-sm text-gray-600">Score</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-4xl font-bold text-green-600">{percent.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Réussite</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-4xl font-bold text-yellow-600">{avgTimePerQuestion.toFixed(1)} min</div>
              <div className="text-sm text-gray-600">Temps moyen/question</div>
            </div>
          </div>
          
          <h3 className="text-xl font-semibold mb-4">Détail des réponses</h3>
          
          <div className="space-y-4">
            {exam.questions.map((question, index) => {
              const userAnswer = selectedAnswers[index];
              const isCorrect = userAnswer === question.correctAnswer;
              
              return (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    isCorrect ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                      isCorrect ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                    }`}>
                      {isCorrect ? '✓' : '✗'}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 mb-2">{question.text}</p>
                      <p className="text-sm text-gray-600">
                        Votre réponse: {question.options[userAnswer] || 'Non répondu'} 
                        {!isCorrect && ` | Bonne réponse: ${question.options[question.correctAnswer]}`}
                      </p>
                      <div className="mt-2 p-3 bg-white rounded border border-gray-200">
                        <p className="text-sm text-gray-700">{question.explanation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // Examen en cours
  const currentQuestion = exam.questions[currentQuestionIndex];
  const progress = Object.keys(selectedAnswers).length;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Barre info + chronomètre */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">{exam.title}</h2>
            <p className="text-sm text-gray-600">
              Question {currentQuestionIndex + 1} / {exam.questions.length} • 
              Répondues: {progress}/{exam.questions.length}
            </p>
          </div>
          
          <div className={`text-2xl font-mono font-bold ${
            timeRemaining < 300 ? 'text-red-600' : 'text-gray-900'
          }`}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        </div>
      </div>

      {/* Question (sans explication) */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-primary-100 text-primary-700">
            {(currentQuestion.module_id || 'module').replace('_', ' ').toUpperCase()}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {currentQuestion.text}
        </h3>

        <div className="space-y-2">
          {currentQuestion.options.map((option, index) => {
            const isSelected = selectedAnswers[currentQuestionIndex] === index;
            
            return (
              <button
                key={index}
                onClick={() => handleSelectAnswer(currentQuestionIndex, index)}
                className={`w-full text-left px-4 py-3 border-2 rounded-lg transition ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-primary-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center font-semibold text-sm ${
                    isSelected ? 'bg-primary-600 text-white border-primary-600' : ''
                  }`}>
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span>{option}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Navigation questions */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h4 className="font-semibold text-gray-900 mb-3">Navigation rapide</h4>
        <div className="grid grid-cols-10 gap-2">
          {exam.questions.map((_, index) => {
            const isAnswered = selectedAnswers.hasOwnProperty(index);
            const isCurrent = index === currentQuestionIndex;
            
            return (
              <button
                key={index}
                onClick={() => handleNavigate(index)}
                className={`w-full aspect-square rounded flex items-center justify-center text-sm font-semibold transition ${
                  isCurrent ? 'ring-2 ring-primary-600 ring-offset-2' : ''
                } ${
                  isAnswered
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                {index + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Contrôles */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => handleNavigate(Math.max(0, currentQuestionIndex - 1))}
          disabled={currentQuestionIndex === 0}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 transition"
        >
          ← Précédente
        </button>
        
        {currentQuestionIndex === exam.questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            className="px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-semibold"
          >
            Terminer l'examen ({progress}/{exam.questions.length} répondues)
          </button>
        ) : (
          <button
            onClick={() => handleNavigate(Math.min(exam.questions.length - 1, currentQuestionIndex + 1))}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            Suivante →
          </button>
        )}
      </div>
    </div>
  );
}

