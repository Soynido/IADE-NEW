/**
 * PDFViewerSimple - Viewer simplifié avec fallback natif
 * Solution pour compatibilité mobile et PDFs volumineux
 */

import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export function PDFViewerSimple() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const pdfFile = searchParams.get('pdf') || 'Prepaconcoursiade-Complet.pdf';
  const targetPage = Number(searchParams.get('page')) || 1;

  const pdfPath = `/pdfs/${pdfFile}`;

  useEffect(() => {
    // Sur mobile, ouvre directement le PDF natif
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    if (isMobile) {
      // Ouvre le PDF en natif (meilleure performance sur mobile)
      window.location.href = `${pdfPath}#page=${targetPage}`;
    }
  }, [pdfPath, targetPage]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-6 sm:p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">📚</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Ouverture du cours
          </h1>
          <p className="text-gray-600">
            {pdfFile.replace('.pdf', '')}
          </p>
        </div>

        {/* Instructions */}
        <div className="space-y-4 mb-8">
          <div className="bg-primary-50 border-l-4 border-primary-500 p-4 rounded">
            <p className="text-sm font-semibold text-primary-800 mb-2">
              📍 Page recommandée : {targetPage}
            </p>
            <p className="text-xs text-primary-700">
              Le PDF va s'ouvrir dans votre lecteur par défaut.
              Naviguez vers la page {targetPage} pour le contenu lié à cette question.
            </p>
          </div>

          <div className="bg-blue-50 p-4 rounded">
            <p className="text-sm font-semibold text-blue-800 mb-2">
              💡 Astuce
            </p>
            <p className="text-xs text-blue-700">
              Sur mobile : utilisez les commandes de votre lecteur PDF pour naviguer.
              Sur desktop : le PDF s'ouvrira directement à la bonne page.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            ← Retour
          </button>

          <a
            href={`${pdfPath}#page=${targetPage}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium text-center"
          >
            Ouvrir le PDF →
          </a>
        </div>

        {/* Info desktop */}
        <div className="mt-6 p-4 bg-gray-50 rounded text-center">
          <p className="text-xs text-gray-600">
            <span className="hidden sm:inline">
              Le PDF s'ouvrira dans un nouvel onglet à la page {targetPage}.
            </span>
            <span className="sm:hidden">
              Sur mobile, le PDF s'ouvrira dans votre application par défaut.
            </span>
          </p>
        </div>

        {/* Fallback iframe pour desktop */}
        <div className="mt-8 hidden lg:block">
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden" style={{ height: '600px' }}>
            <iframe
              src={`${pdfPath}#page=${targetPage}&view=FitH`}
              width="100%"
              height="100%"
              title={`PDF Viewer - ${pdfFile}`}
              className="border-0"
            />
          </div>
          <p className="text-xs text-gray-500 text-center mt-2">
            Prévisualisation desktop - Page {targetPage}
          </p>
        </div>
      </div>
    </div>
  );
}

