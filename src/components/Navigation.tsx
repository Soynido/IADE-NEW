/**
 * Composant Navigation - Menu de navigation principal
 * Tâche [044] - Phase 6 : Frontend Core
 */

import { Link, useLocation } from 'react-router-dom';

export function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Accueil', icon: '🏠' },
    { path: '/revision', label: 'Révision', icon: '📚' },
    { path: '/entrainement', label: 'Entraînement', icon: '💪' },
    { path: '/concours', label: 'Concours Blanc', icon: '🎯' },
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary-600">IADE</span>
            <span className="text-sm text-gray-500">Prépa Concours</span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-2">
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
      </div>
    </nav>
  );
}

