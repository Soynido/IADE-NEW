import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF.js worker (production-ready)
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export function PDFViewer() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const pageContainerRef = useRef<HTMLDivElement>(null);

  const pdfFile = searchParams.get('pdf') || 'Prepaconcoursiade-Complet.pdf';
  const targetPage = Number(searchParams.get('page')) || 1;

  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(targetPage);
  const [scale, setScale] = useState<number>(1.0);
  const [loading, setLoading] = useState(true);

  const pdfPath = `/pdfs/${pdfFile}`;

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setLoading(false);
    
    // Scroll automatique vers la page cible
    setTimeout(() => {
      scrollToPage(targetPage);
    }, 500);
  }

  function scrollToPage(pageNum: number) {
    if (pageContainerRef.current) {
      const pageElement = pageContainerRef.current.querySelector(`[data-page-number="${pageNum}"]`);
      if (pageElement) {
        pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  // Détecte la largeur écran pour adapter le scale
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < 640) {
        setScale(0.5); // Mobile
      } else if (width < 1024) {
        setScale(0.75); // Tablet
      } else {
        setScale(1.0); // Desktop
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' && currentPage > 1) {
        setCurrentPage(currentPage - 1);
        scrollToPage(currentPage - 1);
      } else if (e.key === 'ArrowRight' && currentPage < numPages) {
        setCurrentPage(currentPage + 1);
        scrollToPage(currentPage + 1);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentPage, numPages]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header fixe */}
      <div className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-700 hover:text-primary-600"
          >
            <span className="text-xl">←</span>
            <span className="hidden sm:inline">Retour</span>
          </button>

          <div className="flex-1 text-center">
            <h1 className="text-sm sm:text-lg font-semibold text-gray-800 truncate">
              {(pdfFile || 'document').replace('.pdf', '')}
            </h1>
            <p className="text-xs text-gray-500">
              Page {currentPage} / {numPages || '...'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* Zoom controls */}
            <button
              onClick={() => setScale(Math.max(0.5, scale - 0.1))}
              className="p-2 bg-gray-200 hover:bg-gray-300 rounded"
              title="Zoom out"
            >
              <span className="text-lg">−</span>
            </button>
            <button
              onClick={() => setScale(Math.min(2.0, scale + 0.1))}
              className="p-2 bg-gray-200 hover:bg-gray-300 rounded"
              title="Zoom in"
            >
              <span className="text-lg">+</span>
            </button>
          </div>
        </div>

        {/* Navigation pages */}
        <div className="border-t px-4 py-2 flex items-center justify-center gap-4">
          <button
            onClick={() => {
              if (currentPage > 1) {
                setCurrentPage(currentPage - 1);
                scrollToPage(currentPage - 1);
              }
            }}
            disabled={currentPage <= 1}
            className="px-3 py-1 bg-primary-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-primary-700"
          >
            ← Précédent
          </button>

          <input
            type="number"
            min={1}
            max={numPages}
            value={currentPage}
            onChange={(e) => {
              const page = Number(e.target.value);
              if (page >= 1 && page <= numPages) {
                setCurrentPage(page);
                scrollToPage(page);
              }
            }}
            className="w-16 px-2 py-1 text-center border border-gray-300 rounded"
          />

          <button
            onClick={() => {
              if (currentPage < numPages) {
                setCurrentPage(currentPage + 1);
                scrollToPage(currentPage + 1);
              }
            }}
            disabled={currentPage >= numPages}
            className="px-3 py-1 bg-primary-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-primary-700"
          >
            Suivant →
          </button>
        </div>
      </div>

      {/* Contenu PDF */}
      <div className="max-w-7xl mx-auto py-6 px-2 sm:px-4">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Chargement du PDF...</p>
            </div>
          </div>
        )}

        <div ref={pageContainerRef} className="bg-white shadow-lg rounded-lg overflow-hidden">
          <Document
            file={pdfPath}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(error) => {
              console.error('Erreur chargement PDF:', error);
              console.error('Path:', pdfPath);
              console.error('File:', pdfFile);
              setLoading(false);
            }}
            loading={<div className="p-8 text-center">Chargement...</div>}
            error={
              <div className="p-8 text-center">
                <p className="text-red-600 font-semibold">Erreur de chargement du PDF</p>
                <p className="text-gray-600 mt-2">{pdfFile}</p>
                <p className="text-xs text-gray-500 mt-1">Path: {pdfPath}</p>
                <p className="text-xs text-gray-400 mt-2">
                  Les PDFs volumineux peuvent prendre du temps à charger.
                  Vérifiez votre connexion internet.
                </p>
                <button
                  onClick={() => navigate(-1)}
                  className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                >
                  Retour
                </button>
              </div>
            }
            options={{
              cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/',
              cMapPacked: true,
              standardFontDataUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/standard_fonts/',
            }}
          >
            {Array.from(new Array(numPages), (_, index) => (
              <div
                key={`page_${index + 1}`}
                data-page-number={index + 1}
                className={`mb-4 ${currentPage === index + 1 ? 'ring-4 ring-primary-500' : ''}`}
              >
                <Page
                  pageNumber={index + 1}
                  scale={scale}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  className="mx-auto"
                />
                <div className="text-center py-2 text-sm text-gray-600 bg-gray-50">
                  Page {index + 1}
                </div>
              </div>
            ))}
          </Document>
        </div>
      </div>
    </div>
  );
}

