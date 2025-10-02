import React, { useState } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Reports from './pages/Reports';

type Page = 'dashboard' | 'projects' | 'reports';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <Projects />;
      case 'reports':
        return <Reports />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>🤑 MoneySplit</h1>
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
        </nav>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
