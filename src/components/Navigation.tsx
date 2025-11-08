/**
 * Composant Navigation - Menu de navigation principal
 * Tâche [044] - Phase 6 : Frontend Core
 */

import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

export function Navigation() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Accueil', icon: '🏠' },
    { path: '/revision', label: 'Révision', icon: '📚' },
    { path: '/entrainement', label: 'Entraînement', icon: '💪' },
    { path: '/concours', label: 'Concours Blanc', icon: '🎯' },
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  ];

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-xl md:text-2xl font-bold text-primary-600">IADE</span>
            <span className="hidden sm:inline text-sm text-gray-500">Prépa Concours</span>
          </Link>

          {/* Burger Menu (Mobile) */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-600 hover:text-gray-900"
            aria-label="Menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Navigation Desktop */}
          <div className="hidden md:flex items-center gap-2">
            {navItems.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-lg transition ${
                  isActive(item.path)
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Navigation Mobile */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4">
            <div className="flex flex-col gap-2">
              <Link
                to="/revision"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-4 py-3 rounded-lg text-center transition ${
                  location.pathname === '/revision'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📖 Révision
              </Link>
              <Link
                to="/entrainement"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-4 py-3 rounded-lg text-center transition ${
                  location.pathname === '/entrainement'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                🎯 Entraînement
              </Link>
              <Link
                to="/concours"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-4 py-3 rounded-lg text-center transition ${
                  location.pathname === '/concours'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                ⏱️ Concours
              </Link>
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-4 py-3 rounded-lg text-center transition ${
                  location.pathname === '/dashboard'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📊 Dashboard
              </Link>
              
              {attempts > 0 && (
                <div className="mt-2 px-4 py-2 bg-green-50 rounded-lg text-center">
                  <div className="text-sm text-gray-600">Score global</div>
                  <div className="text-xl font-bold text-green-600">
                    {Math.round((correct / attempts) * 100)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

