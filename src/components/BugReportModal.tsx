/**
 * Modal de rapport de bug
 * Interface pour permettre aux utilisateurs de signaler des problèmes
 */

import { useState } from 'react';
import { BugCategory, BugReportFormData } from '@/types/bugReport';
import { Question } from '@/types';

interface BugReportModalProps {
  question: Question;
  mode: 'revision' | 'entrainement' | 'concours';
  userAnswer?: number;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (report: BugReportFormData) => Promise<void>;
}

const BUG_CATEGORIES: Array<{ value: BugCategory; label: string; icon: string; description: string }> = [
  {
    value: 'reponse_incorrecte',
    label: 'Réponse incorrecte',
    icon: '❌',
    description: 'La réponse marquée comme correcte est fausse'
  },
  {
    value: 'plusieurs_reponses',
    label: 'Plusieurs réponses possibles',
    icon: '🔀',
    description: 'Plusieurs options semblent correctes'
  },
  {
    value: 'question_ambigue',
    label: 'Question ambiguë',
    icon: '❓',
    description: 'Question mal formulée ou pas claire'
  },
  {
    value: 'explication_incorrecte',
    label: 'Explication erronée',
    icon: '📝',
    description: "L'explication contient des erreurs"
  },
  {
    value: 'explication_manquante',
    label: 'Explication incomplète',
    icon: '📄',
    description: "L'explication manque de détails"
  },
  {
    value: 'reference_incorrecte',
    label: 'Lien cours incorrect',
    icon: '🔗',
    description: 'La page de cours indiquée est fausse'
  },
  {
    value: 'terme_medical_incorrect',
    label: 'Terme médical erroné',
    icon: '⚕️',
    description: 'Erreur dans un terme biomédical'
  },
  {
    value: 'faute_orthographe',
    label: 'Faute de français',
    icon: '✏️',
    description: 'Faute d\'orthographe ou grammaire'
  },
  {
    value: 'options_repetees',
    label: 'Options similaires',
    icon: '🔁',
    description: 'Options en double ou trop proches'
  },
  {
    value: 'difficulte_mal_calibree',
    label: 'Difficulté inadaptée',
    icon: '⚖️',
    description: 'La difficulté ne correspond pas'
  },
  {
    value: 'hors_programme',
    label: 'Hors programme',
    icon: '🚫',
    description: 'Question hors du programme IADE'
  },
  {
    value: 'autre',
    label: 'Autre problème',
    icon: '💬',
    description: 'Un autre type de problème'
  }
];

export function BugReportModal({
  question,
  mode,
  userAnswer,
  isOpen,
  onClose,
  onSubmit
}: BugReportModalProps) {
  // ✅ v2.0 : Multi-catégories
  const [categories, setCategories] = useState<BugCategory[]>([]);
  const [description, setDescription] = useState('');
  const [suggestedFix, setSuggestedFix] = useState('');
  const [expectedAnswer, setExpectedAnswer] = useState<number | undefined>(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  if (!isOpen) return null;

  // ✅ v2.0 : Toggle catégorie (multi-sélection)
  const toggleCategory = (cat: BugCategory) => {
    if (categories.includes(cat)) {
      setCategories(categories.filter(c => c !== cat));
    } else {
      setCategories([...categories, cat]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // ✅ v2.0 : Au moins une catégorie + description
    if (categories.length === 0 || !description.trim()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const reportData: BugReportFormData = {
        categories,  // ✅ Plusieurs catégories
        description: description.trim(),
        suggestedFix: suggestedFix.trim() || undefined,
        expectedAnswer
      };

      await onSubmit(reportData);
      
      setShowSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 2000);
    } catch (error) {
      console.error('Erreur envoi rapport bug:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setCategories([]);
    setDescription('');
    setSuggestedFix('');
    setExpectedAnswer(undefined);
    setShowSuccess(false);
    onClose();
  };

  const requiresExpectedAnswer = 
    categories.includes('reponse_incorrecte') || 
    categories.includes('plusieurs_reponses');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-orange-500 p-6 text-white">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">🐛 Signaler un problème</h2>
              <p className="text-red-100 text-sm">
                Aidez-nous à améliorer la qualité des questions
              </p>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-red-100 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {showSuccess ? (
          /* Message de succès */
          <div className="p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-2xl font-bold text-green-600 mb-2">
              Merci !
            </h3>
            <p className="text-gray-600">
              Votre signalement a été enregistré et sera analysé par notre IA.
            </p>
          </div>
        ) : (
          /* Formulaire */
          <form onSubmit={handleSubmit} className="p-6">
            {/* Info question */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-2">Question concernée :</p>
              <p className="font-medium text-gray-900 line-clamp-2">
                {question.text}
              </p>
              <div className="flex gap-2 mt-2 text-xs text-gray-500">
                <span className="px-2 py-1 bg-white rounded">
                  {(question.module_id || 'module').replace('_', ' ').toUpperCase()}
                </span>
                <span className="px-2 py-1 bg-white rounded">
                  Mode: {mode}
                </span>
              </div>
            </div>

            {/* Sélection catégories (multi-sélection) */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Type(s) de problème(s) * 
                <span className="text-gray-500 font-normal ml-2">
                  (Vous pouvez en sélectionner plusieurs)
                </span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                {BUG_CATEGORIES.map((cat) => {
                  const isSelected = categories.includes(cat.value);
                  return (
                    <label
                      key={cat.value}
                      className={`p-3 rounded-lg border-2 text-left transition cursor-pointer ${
                        isSelected
                          ? 'border-red-500 bg-red-50'
                          : 'border-gray-200 hover:border-red-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleCategory(cat.value)}
                          className="mt-1 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl">{cat.icon}</span>
                            <span className="font-medium text-sm">{cat.label}</span>
                          </div>
                          <p className="text-xs text-gray-500">{cat.description}</p>
                        </div>
                      </div>
                    </label>
                  );
                })}
              </div>
              {categories.length > 0 && (
                <p className="mt-2 text-sm text-green-600 font-medium">
                  ✓ {categories.length} problème{categories.length > 1 ? 's' : ''} sélectionné{categories.length > 1 ? 's' : ''}
                </p>
              )}
            </div>

            {/* Bonne réponse attendue (si applicable) */}
            {requiresExpectedAnswer && categories.length > 0 && (
              <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Quelle est la bonne réponse selon vous ?
                </label>
                <div className="space-y-2">
                  {question.options.map((option, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => setExpectedAnswer(index)}
                      className={`w-full p-3 rounded-lg border-2 text-left transition ${
                        expectedAnswer === index
                          ? 'border-yellow-500 bg-yellow-100'
                          : 'border-gray-300 hover:border-yellow-400 bg-white'
                      }`}
                    >
                      <span className="font-medium mr-2">{String.fromCharCode(65 + index)}.</span>
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Description détaillée */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Description du problème *
                {categories.length > 1 && (
                  <span className="text-gray-500 font-normal ml-2">
                    (Précisez chaque problème)
                  </span>
                )}
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={categories.length > 0
                  ? `Décrivez les problèmes sélectionnés :\n${categories.map(c => `• ${BUG_CATEGORIES.find(cat => cat.value === c)?.label}`).join('\n')}`
                  : "Expliquez en détail le ou les problème(s) rencontré(s)..."
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                rows={5}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                💡 Astuce : Si plusieurs problèmes, décrivez-les point par point
              </p>
            </div>

            {/* Suggestion de correction */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Votre suggestion de correction (optionnel)
              </label>
              <textarea
                value={suggestedFix}
                onChange={(e) => setSuggestedFix(e.target.value)}
                placeholder="Comment corrigeriez-vous cette question ? (optionnel)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                rows={3}
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                disabled={isSubmitting}
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={categories.length === 0 || !description.trim() || isSubmitting}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:from-red-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition font-semibold"
              >
                {isSubmitting ? 'Envoi en cours...' : 'Envoyer le signalement'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

