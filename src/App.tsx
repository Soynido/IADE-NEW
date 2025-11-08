/**
 * App principale avec routing
 * Tâche [044] - Phase 6 : Frontend Core
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { RevisionMode } from './components/RevisionMode';
import { TrainingMode } from './components/TrainingMode';
import { ExamMode } from './components/ExamMode';
import { Dashboard as DashboardComponent } from './components/Dashboard';
import { PDFViewerSimple } from './components/PDFViewerSimple';

// Page d'accueil
function HomePage() {
  return (
    <div className="container mx-auto px-4 py-16 max-w-4xl">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          IADE
        </h1>
        <p className="text-xl text-gray-600">
          Simulateur d'apprentissage intégral pour la préparation au concours IADE
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Révision */}
        <a
          href="/revision"
          className="block p-8 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:shadow-xl transition border-2 border-blue-200"
        >
          <div className="text-5xl mb-4">📚</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Révision</h3>
          <p className="text-gray-600">
            Apprenez à votre rythme avec des explications immédiates
          </p>
        </a>

        {/* Entraînement */}
        <a
          href="/entrainement"
          className="block p-8 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:shadow-xl transition border-2 border-green-200"
        >
          <div className="text-5xl mb-4">💪</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Entraînement</h3>
          <p className="text-gray-600">
            Sessions de 10 questions adaptatives avec feedback
          </p>
        </a>

        {/* Concours Blanc */}
        <a
          href="/concours"
          className="block p-8 bg-gradient-to-br from-red-50 to-red-100 rounded-xl hover:shadow-xl transition border-2 border-red-200"
        >
          <div className="text-5xl mb-4">🎯</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Concours Blanc</h3>
          <p className="text-gray-600">
            Examens de 60 questions en conditions réelles
          </p>
        </a>
      </div>

      {/* Stats rapides */}
      <div className="mt-12 p-6 bg-white rounded-xl shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistiques</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-3xl font-bold text-primary-600">2000+</div>
            <div className="text-sm text-gray-600">Questions validées</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">14</div>
            <div className="text-sm text-gray-600">Modules thématiques</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">6</div>
            <div className="text-sm text-gray-600">Examens blancs</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Page liste des examens
function ExamsList() {
  const exams = [
    { id: 'exam_01_physio_pharma', title: 'Examen 1 : Physiologie & Pharmacologie' },
    { id: 'exam_02_cardio_rea', title: 'Examen 2 : Cardio & Réanimation' },
    { id: 'exam_03_resp_vent', title: 'Examen 3 : Respiratoire & Ventilation' },
    { id: 'exam_04_pharmaco', title: 'Examen 4 : Pharmacologie Complète' },
    { id: 'exam_05_alr_douleur', title: 'Examen 5 : ALR & Douleur' },
    { id: 'exam_06_mixte', title: 'Examen 6 : Mixte Complet' },
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Examens Blancs</h1>
      <div className="grid md:grid-cols-2 gap-6">
        {exams.map(exam => (
          <a
            key={exam.id}
            href={`/concours/${exam.id}`}
            className="block p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition border-2 border-gray-200 hover:border-primary-500"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{exam.title}</h3>
            <p className="text-sm text-gray-600">60 questions • 120 minutes</p>
          </a>
        ))}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/revision" element={<RevisionMode />} />
          <Route path="/entrainement" element={<TrainingMode />} />
          <Route path="/concours" element={<ExamsList />} />
          <Route path="/concours/:examId" element={<ExamMode />} />
          <Route path="/dashboard" element={<DashboardComponent />} />
          <Route path="/pdf-viewer" element={<PDFViewerSimple />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App

