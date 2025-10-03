import React, { useState, useEffect } from 'react';
import './App.css';
import TaxCalculator from './pages/TaxCalculator';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Reports from './pages/Reports';
import RecordsManagement from './pages/RecordsManagement';
import TaxBracketsManagement from './pages/TaxBracketsManagement';
import Analytics from './pages/Analytics';

type Page = 'calculator' | 'dashboard' | 'projects' | 'reports' | 'records' | 'tax-brackets' | 'analytics';

interface PrefilledProjectData {
  revenue: number;
  costs: number;
  numPeople: number;
  country: string;
  taxType: 'Individual' | 'Business';
  distributionMethod: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('calculator');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [prefilledProject, setPrefilledProject] = useState<PrefilledProjectData | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);

  const navigateToProjects = (data: PrefilledProjectData) => {
    setPrefilledProject(data);
    setCurrentPage('projects');
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Esc to close modal
      if (e.key === 'Escape') {
        setShowShortcuts(false);
        return;
      }

      // Only trigger if Ctrl/Cmd is pressed
      if (!(e.ctrlKey || e.metaKey)) return;

      switch(e.key) {
        case '1':
          e.preventDefault();
          setCurrentPage('calculator');
          break;
        case '2':
          e.preventDefault();
          setCurrentPage('dashboard');
          break;
        case '3':
          e.preventDefault();
          setCurrentPage('projects');
          break;
        case '4':
          e.preventDefault();
          setCurrentPage('analytics');
          break;
        case '5':
          e.preventDefault();
          setCurrentPage('reports');
          break;
        case 'k':
          e.preventDefault();
          setShowShortcuts(prev => !prev);
          break;
        case 'b':
          e.preventDefault();
          setSidebarCollapsed(prev => !prev);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'calculator':
        return <TaxCalculator onCreateProject={navigateToProjects} />;
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <Projects prefilledData={prefilledProject} />;
      case 'reports':
        return <Reports />;
      case 'records':
        return <RecordsManagement />;
      case 'tax-brackets':
        return <TaxBracketsManagement />;
      case 'analytics':
        return <Analytics />;
      default:
        return <TaxCalculator onCreateProject={navigateToProjects} />;
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
            className={`nav-item ${currentPage === 'calculator' ? 'active' : ''}`}
            onClick={() => setCurrentPage('calculator')}
          >
            <span>💡</span>
            <span>Tax Calculator</span>
          </div>
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
            className={`nav-item ${currentPage === 'analytics' ? 'active' : ''}`}
            onClick={() => setCurrentPage('analytics')}
          >
            <span>📊</span>
            <span>Analytics</span>
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

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowShortcuts(false)}>
          <div className="card" style={{ maxWidth: '500px', width: '90%' }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3>⌨️ Keyboard Shortcuts</h3>
              <button onClick={() => setShowShortcuts(false)} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
            </div>

            <div style={{ display: 'grid', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Tax Calculator</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + 1</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Dashboard</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + 2</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>New Project</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + 3</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Analytics</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + 4</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Reports</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + 5</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Toggle Sidebar</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + B</kbd>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
                <span>Show Shortcuts</span>
                <kbd style={{ background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Ctrl/Cmd + K</kbd>
              </div>
            </div>

            <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px', color: '#718096' }}>
              Press <kbd style={{ background: '#e2e8f0', padding: '2px 6px', borderRadius: '3px' }}>Esc</kbd> or click outside to close
            </div>
          </div>
        </div>
      )}

      {/* Shortcuts hint */}
      <div style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        background: 'rgba(102, 126, 234, 0.9)',
        color: 'white',
        padding: '8px 16px',
        borderRadius: '20px',
        fontSize: '12px',
        cursor: 'pointer',
        zIndex: 999
      }} onClick={() => setShowShortcuts(true)}>
        Press <kbd style={{ background: 'rgba(255,255,255,0.3)', padding: '2px 6px', borderRadius: '3px' }}>Ctrl+K</kbd> for shortcuts
      </div>
    </div>
  );
}

export default App;
