import React, { useState, useEffect } from "react";
import "./App.css";
import TaxCalculator from "./pages/TaxCalculator";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import Reports from "./pages/Reports";
import RecordsManagement from "./pages/RecordsManagement";
import TaxBracketsManagement from "./pages/TaxBracketsManagement";
import Analytics from "./pages/Analytics";

type Page = "calculator" | "dashboard" | "projects" | "reports" | "records" | "tax-brackets" | "analytics";

interface PrefilledProjectData {
  revenue: number;
  costs: number;
  numPeople: number;
  country: string;
  taxType: "Individual" | "Business";
  distributionMethod: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("calculator");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [prefilledProject, setPrefilledProject] = useState<PrefilledProjectData | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showWelcome, setShowWelcome] = useState(() => {
    return !localStorage.getItem("moneysplit-welcomed");
  });

  const navigateToProjects = (data: PrefilledProjectData) => {
    setPrefilledProject(data);
    setCurrentPage("projects");
  };

  const dismissWelcome = () => {
    setShowWelcome(false);
    localStorage.setItem("moneysplit-welcomed", "true");
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Esc to close modals
      if (e.key === "Escape") {
        setShowShortcuts(false);
        setShowHelp(false);
        return;
      }

      // Only trigger if Ctrl/Cmd is pressed
      if (!(e.ctrlKey || e.metaKey)) {
        return;
      }

      switch (e.key) {
        case "1":
          e.preventDefault();
          setCurrentPage("calculator");
          break;
        case "2":
          e.preventDefault();
          setCurrentPage("dashboard");
          break;
        case "3":
          e.preventDefault();
          setCurrentPage("projects");
          break;
        case "4":
          e.preventDefault();
          setCurrentPage("analytics");
          break;
        case "5":
          e.preventDefault();
          setCurrentPage("reports");
          break;
        case "k":
          e.preventDefault();
          setShowShortcuts(prev => !prev);
          break;
        case "b":
          e.preventDefault();
          setSidebarCollapsed(prev => !prev);
          break;
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, []);

  const helpContent: Record<Page, { title: string; tips: string[] }> = {
    calculator: {
      title: "💡 Tax Calculator Help",
      tips: [
        "Enter your project revenue and costs to see all tax strategies",
        "Select your country - we support US (with state taxes), UK, Canada, and Spain",
        "The optimal strategy is highlighted with a green border",
        "Click the ⭐ to favorite strategies you use often",
        'Click "Create Project" to save your calculation',
      ],
    },
    dashboard: {
      title: "📊 Dashboard Help",
      tips: [
        "View your recent projects and overall statistics",
        "The optimization column shows if you chose the best tax strategy",
        "Green checkmark (✅) means you made the optimal choice",
        "Red indicator (💡) shows how much you could have saved",
      ],
    },
    projects: {
      title: "📁 New Project Help",
      tips: [
        "Fill in project details and team member information",
        "Work shares must add up to 1.0 (100%)",
        "For US/Spain, see tax comparison below the form",
        "Use pre-filled data from Tax Calculator for quick setup",
      ],
    },
    analytics: {
      title: "📊 Analytics Help",
      tips: [
        "View aggregate statistics across all your projects",
        "Export your data in CSV, JSON, or PDF format",
        "Import historical data using CSV upload",
        "Strategy effectiveness shows which approaches work best",
      ],
    },
    reports: {
      title: "📈 Reports Help",
      tips: [
        "Generate detailed visualizations of your tax data",
        "Charts open in a new browser tab",
        "Use revenue forecasting to plan ahead",
      ],
    },
    records: {
      title: "📋 Records Management Help",
      tips: [
        "View and manage all your saved calculations",
        "Edit or delete individual records",
        "Click on a record to see full details",
      ],
    },
    "tax-brackets": {
      title: "💼 Tax Brackets Help",
      tips: [
        "Manage custom tax brackets for any country",
        "Add new brackets or modify existing ones",
        "Changes affect future calculations only",
      ],
    },
  };

  const renderPage = () => {
    switch (currentPage) {
      case "calculator":
        return <TaxCalculator onCreateProject={navigateToProjects} />;
      case "dashboard":
        return <Dashboard />;
      case "projects":
        return <Projects prefilledData={prefilledProject} />;
      case "reports":
        return <Reports />;
      case "records":
        return <RecordsManagement />;
      case "tax-brackets":
        return <TaxBracketsManagement />;
      case "analytics":
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
        <button
          onClick={() => setShowHelp(true)}
          style={{
            position: "absolute",
            right: "20px",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            border: "none",
            borderRadius: "50%",
            width: "40px",
            height: "40px",
            fontSize: "20px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            transition: "transform 0.2s",
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.1)"}
          onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
          title="Help & Guide"
        >
          ?
        </button>
      </div>
      <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        <h1><span className="logo-emoji">💰</span>MoneySplit</h1>
        <nav className="nav-menu">
          <div
            className={`nav-item ${currentPage === "calculator" ? "active" : ""}`}
            onClick={() => setCurrentPage("calculator")}
          >
            <span>💡</span>
            <span>Tax Calculator</span>
          </div>
          <div
            className={`nav-item ${currentPage === "dashboard" ? "active" : ""}`}
            onClick={() => setCurrentPage("dashboard")}
          >
            <span>📊</span>
            <span>Dashboard</span>
          </div>
          <div
            className={`nav-item ${currentPage === "projects" ? "active" : ""}`}
            onClick={() => setCurrentPage("projects")}
          >
            <span>📁</span>
            <span>New Project</span>
          </div>
          <div
            className={`nav-item ${currentPage === "analytics" ? "active" : ""}`}
            onClick={() => setCurrentPage("analytics")}
          >
            <span>📊</span>
            <span>Analytics</span>
          </div>
          <div
            className={`nav-item ${currentPage === "reports" ? "active" : ""}`}
            onClick={() => setCurrentPage("reports")}
          >
            <span>📈</span>
            <span>Reports</span>
          </div>
          <div
            className={`nav-item ${currentPage === "records" ? "active" : ""}`}
            onClick={() => setCurrentPage("records")}
          >
            <span>📋</span>
            <span>Manage Records</span>
          </div>
          <div
            className={`nav-item ${currentPage === "tax-brackets" ? "active" : ""}`}
            onClick={() => setCurrentPage("tax-brackets")}
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
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0,0,0,0.7)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }} onClick={() => setShowShortcuts(false)}>
          <div className="card" style={{ maxWidth: "500px", width: "90%" }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3>⌨️ Keyboard Shortcuts</h3>
              <button onClick={() => setShowShortcuts(false)} style={{ background: "none", border: "none", fontSize: "24px", cursor: "pointer" }}>×</button>
            </div>

            <div style={{ display: "grid", gap: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Tax Calculator</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + 1</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Dashboard</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + 2</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>New Project</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + 3</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Analytics</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + 4</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Reports</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + 5</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Toggle Sidebar</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + B</kbd>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px", background: "#f7fafc", borderRadius: "6px" }}>
                <span>Show Shortcuts</span>
                <kbd style={{ background: "#667eea", color: "white", padding: "4px 8px", borderRadius: "4px", fontSize: "12px" }}>Ctrl/Cmd + K</kbd>
              </div>
            </div>

            <div style={{ marginTop: "20px", textAlign: "center", fontSize: "14px", color: "#718096" }}>
              Press <kbd style={{ background: "#e2e8f0", padding: "2px 6px", borderRadius: "3px" }}>Esc</kbd> or click outside to close
            </div>
          </div>
        </div>
      )}

      {/* Help Modal */}
      {showHelp && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0,0,0,0.7)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }} onClick={() => setShowHelp(false)}>
          <div className="card" style={{ maxWidth: "600px", width: "90%", maxHeight: "80vh", overflow: "auto" }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3>{helpContent[currentPage].title}</h3>
              <button onClick={() => setShowHelp(false)} style={{ background: "none", border: "none", fontSize: "24px", cursor: "pointer" }}>×</button>
            </div>

            <div style={{ marginBottom: "24px" }}>
              <h4 style={{ fontSize: "16px", marginBottom: "12px", color: "#667eea" }}>Quick Tips:</h4>
              <ul style={{ lineHeight: "1.8", paddingLeft: "20px" }}>
                {helpContent[currentPage].tips.map((tip, idx) => (
                  <li key={idx} style={{ marginBottom: "8px" }}>{tip}</li>
                ))}
              </ul>
            </div>

            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "20px" }}>
              <h4 style={{ fontSize: "16px", marginBottom: "12px", color: "#667eea" }}>General Features:</h4>
              <div style={{ display: "grid", gap: "12px" }}>
                <div style={{ padding: "12px", background: "#f7fafc", borderRadius: "6px" }}>
                  <strong>⌨️ Keyboard Shortcuts</strong>
                  <p style={{ fontSize: "14px", color: "#718096", marginTop: "4px" }}>
                    Press <kbd style={{ background: "#667eea", color: "white", padding: "2px 6px", borderRadius: "3px", fontSize: "12px" }}>Ctrl+K</kbd> to see all shortcuts
                  </p>
                </div>
                <div style={{ padding: "12px", background: "#f7fafc", borderRadius: "6px" }}>
                  <strong>🌍 Multi-Country Support</strong>
                  <p style={{ fontSize: "14px", color: "#718096", marginTop: "4px" }}>
                    Calculate taxes for US (with state taxes), UK, Canada, and Spain
                  </p>
                </div>
                <div style={{ padding: "12px", background: "#f7fafc", borderRadius: "6px" }}>
                  <strong>📊 Smart Analytics</strong>
                  <p style={{ fontSize: "14px", color: "#718096", marginTop: "4px" }}>
                    Track your projects and see which tax strategies work best
                  </p>
                </div>
              </div>
            </div>

            <div style={{ marginTop: "20px", textAlign: "center" }}>
              <button
                onClick={() => setShowHelp(false)}
                className="btn btn-primary"
                style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", border: "none" }}
              >
                Got it!
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Banner */}
      {showWelcome && (
        <div style={{
          position: "fixed",
          top: "80px",
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1001,
          width: "90%",
          maxWidth: "600px",
          animation: "slideDown 0.3s ease-out",
        }}>
          <div style={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            padding: "24px",
            borderRadius: "12px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginBottom: "12px", fontSize: "20px" }}>👋 Welcome to MoneySplit!</h3>
                <p style={{ opacity: 0.95, marginBottom: "16px", lineHeight: "1.6" }}>
                  Your smart tax calculator for commission-based income. Calculate taxes across multiple countries,
                  compare strategies, and find the best approach to maximize your take-home income.
                </p>
                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                  <button
                    onClick={() => {
                      setShowHelp(true); dismissWelcome();
                    }}
                    style={{
                      background: "white",
                      color: "#667eea",
                      border: "none",
                      padding: "8px 16px",
                      borderRadius: "6px",
                      fontSize: "14px",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    📚 Show Me Around
                  </button>
                  <button
                    onClick={dismissWelcome}
                    style={{
                      background: "rgba(255,255,255,0.2)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.3)",
                      padding: "8px 16px",
                      borderRadius: "6px",
                      fontSize: "14px",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    ✓ Got it, let's start
                  </button>
                </div>
              </div>
              <button
                onClick={dismissWelcome}
                style={{ background: "none", border: "none", color: "white", fontSize: "24px", cursor: "pointer", marginLeft: "12px" }}
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Shortcuts hint */}
      <div style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        background: "rgba(102, 126, 234, 0.9)",
        color: "white",
        padding: "8px 16px",
        borderRadius: "20px",
        fontSize: "12px",
        cursor: "pointer",
        zIndex: 999,
      }} onClick={() => setShowShortcuts(true)}>
        Press <kbd style={{ background: "rgba(255,255,255,0.3)", padding: "2px 6px", borderRadius: "3px" }}>Ctrl+K</kbd> for shortcuts
      </div>
    </div>
  );
}

export default App;
