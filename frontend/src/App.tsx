import React, { useState } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Reports from './pages/Reports';
import RecordsManagement from './pages/RecordsManagement';
import TaxBracketsManagement from './pages/TaxBracketsManagement';

type Page = 'dashboard' | 'projects' | 'reports' | 'records' | 'tax-brackets';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <Projects />;
      case 'reports':
        return <Reports />;
      case 'records':
        return <RecordsManagement />;
      case 'tax-brackets':
        return <TaxBracketsManagement />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <button
        className="menu-toggle"
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        aria-label="Toggle menu"
      >
        <svg viewBox="0 0 24 24">
          {sidebarCollapsed ? (
            <path d="M3 12h18M3 6h18M3 18h18" strokeLinecap="round" strokeLinejoin="round"/>
          ) : (
            <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round"/>
          )}
        </svg>
      </button>
      <div className="top-logo">
        <span className="top-logo-emoji">💰</span>
        <span className="top-logo-text">MoneySplit</span>
      </div>
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <h1><span className="logo-emoji">💰</span>MoneySplit</h1>
        <nav className="nav-menu">
          <div
            className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            <span>📊</span>
            <span>Dashboard</span>
          </div>
          <div
            className={`nav-item ${currentPage === 'projects' ? 'active' : ''}`}
            onClick={() => setCurrentPage('projects')}
          >
            <span>📁</span>
            <span>New Project</span>
          </div>
          <div
            className={`nav-item ${currentPage === 'reports' ? 'active' : ''}`}
            onClick={() => setCurrentPage('reports')}
          >
            <span>📈</span>
            <span>Reports</span>
          </div>
          <div
            className={`nav-item ${currentPage === 'records' ? 'active' : ''}`}
            onClick={() => setCurrentPage('records')}
          >
            <span>📋</span>
            <span>Manage Records</span>
          </div>
          <div
            className={`nav-item ${currentPage === 'tax-brackets' ? 'active' : ''}`}
            onClick={() => setCurrentPage('tax-brackets')}
          >
            <span>💼</span>
            <span>Tax Brackets</span>
          </div>
        </nav>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
