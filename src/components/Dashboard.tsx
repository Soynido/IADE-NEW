/**
 * Composant Dashboard - Statistiques et Progression
 * Tâches [060-063] - Phase 8 : Dashboard & Analytics
 * 
 * Features:
 * - Score global (correct/attempts)
 * - Jours actifs
 * - Modules faibles (top 5)
 * - Graphique progression (EMA 7 jours)
 * - Historique examens blancs
 */

import { useUserStore } from '@/store/useUserStore';

export function Dashboard() {
  const { stats, getWeakModules, getStreakDays } = useUserStore();
  
  const globalScore = stats.attempts > 0 
    ? (stats.correct / stats.attempts) * 100 
    : 0;
  
  const weakModules = getWeakModules();
  const streakDays = getStreakDays();
  
  // Calcul EMA 7 jours (simplifié pour v1)
  const calculateEMA = () => {
    // TODO: implémenter EMA basé sur historique
    return globalScore;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Tableau de Bord</h1>

      {/* Stats principales */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        {/* Score global */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Score Global</div>
          <div className="text-4xl font-bold text-primary-600 mb-2">
            {globalScore.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-500">
            {stats.correct} / {stats.attempts} réponses correctes
          </div>
        </div>

        {/* Jours actifs */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Jours Actifs</div>
          <div className="text-4xl font-bold text-green-600 mb-2">
            {streakDays}
          </div>
          <div className="text-sm text-gray-500">
            Série en cours
          </div>
        </div>

        {/* Questions répondues */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Questions Répondues</div>
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {stats.attempts}
          </div>
          <div className="text-sm text-gray-500">
            Total
          </div>
        </div>

        {/* Examens passés */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Examens Passés</div>
          <div className="text-4xl font-bold text-purple-600 mb-2">
            {stats.examResults.length}
          </div>
          <div className="text-sm text-gray-500">
            Concours blancs
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Modules faibles */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Modules à Travailler
          </h2>
          
          {weakModules.length > 0 ? (
            <div className="space-y-3">
              {weakModules.map(({ moduleId, score }) => (
                <div key={moduleId}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {(moduleId || 'module').replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">
                      {(score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        score < 0.5 ? 'bg-red-500' :
                        score < 0.7 ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Aucune statistique disponible. Commencez à réviser !
            </p>
          )}
        </div>

        {/* Historique examens */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Historique Examens Blancs
          </h2>
          
          {stats.examResults.length > 0 ? (
            <div className="space-y-3">
              {stats.examResults.slice(0, 5).map((result, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {(result.examId || 'exam').replace(/_/g, ' ').toUpperCase()}
                    </span>
                    <span className={`text-lg font-bold ${
                      result.score >= 80 ? 'text-green-600' :
                      result.score >= 60 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {result.score.toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{new Date(result.date).toLocaleDateString('fr-FR')}</span>
                    <span>•</span>
                    <span>{result.duration} min</span>
                    <span>•</span>
                    <span>{result.totalQuestions} questions</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Aucun examen passé. Passez votre premier concours blanc !
            </p>
          )}
        </div>
      </div>

      {/* Statistiques par module */}
      <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Détails par Module
        </h2>
        
        {Object.keys(stats.byModule).length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Module</th>
                  <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">Tentatives</th>
                  <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">Réussies</th>
                  <th className="px-4 py-2 text-center text-sm font-semibold text-gray-700">Score</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Dernière activité</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.byModule)
                  .sort(([, a], [, b]) => {
                    const scoreA = a.attempts > 0 ? a.correct / a.attempts : 0;
                    const scoreB = b.attempts > 0 ? b.correct / b.attempts : 0;
                    return scoreB - scoreA;
                  })
                  .map(([moduleId, data]) => {
                    const score = data.attempts > 0 ? (data.correct / data.attempts) * 100 : 0;
                    
                    return (
                      <tr key={moduleId} className="border-t border-gray-200">
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {(moduleId || 'module').replace('_', ' ').toUpperCase()}
                        </td>
                        <td className="px-4 py-3 text-sm text-center text-gray-700">
                          {data.attempts}
                        </td>
                        <td className="px-4 py-3 text-sm text-center text-gray-700">
                          {data.correct}
                        </td>
                        <td className="px-4 py-3 text-sm text-center">
                          <span className={`font-semibold ${
                            score >= 80 ? 'text-green-600' :
                            score >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {score.toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {new Date(data.lastSeen).toLocaleDateString('fr-FR')}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            Aucune donnée disponible. Commencez à vous entraîner !
          </p>
        )}
      </div>
    </div>
  );
}

