import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface AnalyticsSummary {
  total_projects: number;
  total_revenue: number;
  total_tax_paid: number;
  total_take_home: number;
  avg_effective_rate: number;
  top_strategy: string;
  avg_project_revenue: number;
  avg_tax_per_project: number;
}

interface Strategy {
  strategy: string;
  count: number;
  total_revenue: number;
  total_tax: number;
  avg_effective_rate: number;
  avg_take_home: number;
}

const Analytics: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState<string>('');

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const [summaryRes, strategyRes] = await Promise.all([
          axios.get('http://localhost:8000/api/analytics/summary'),
          axios.get('http://localhost:8000/api/analytics/strategy-effectiveness')
        ]);

        setSummary(summaryRes.data);
        setStrategies(strategyRes.data.strategies);
      } catch (error) {
        console.error('Error loading analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  const formatCurrency = (amount: number) => {
    return `$${Math.floor(amount).toLocaleString()}`;
  };

  const handleImportCSV = async () => {
    if (!importFile) return;

    setImporting(true);
    setImportMessage('');

    try {
      const formData = new FormData();
      formData.append('file', importFile);

      const response = await axios.post('http://localhost:8000/api/import-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000
      });

      setImportMessage(`✅ Success! Imported ${response.data.records_created} records`);
      setImportFile(null);

      // Reload analytics after import
      const [summaryRes, strategyRes] = await Promise.all([
        axios.get('http://localhost:8000/api/analytics/summary'),
        axios.get('http://localhost:8000/api/analytics/strategy-effectiveness')
      ]);
      setSummary(summaryRes.data);
      setStrategies(strategyRes.data.strategies);
    } catch (error: any) {
      setImportMessage(`❌ Import failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setImporting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="alert alert-error">
        Failed to load analytics data
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ flex: 1 }}>
          <h2>📊 Analytics Dashboard</h2>
          <p>Insights from your tax optimization history</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <a
            href="http://localhost:8000/api/export-csv"
            download
            className="btn btn-primary"
            style={{ textDecoration: 'none', display: 'inline-block' }}
          >
            📥 Export CSV
          </a>
          <a
            href="http://localhost:8000/api/export-json"
            download
            className="btn btn-primary"
            style={{ textDecoration: 'none', display: 'inline-block', background: '#764ba2' }}
          >
            📥 Export JSON
          </a>
          <a
            href="http://localhost:8000/api/export/forecast/pdf?current_revenue=100000&growth_rate=0.1&quarters=4&country=US"
            download
            className="btn btn-primary"
            style={{ textDecoration: 'none', display: 'inline-block', background: '#e53e3e' }}
          >
            📄 Export PDF
          </a>
        </div>
      </div>

      {/* CSV Import Section */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)', color: 'white' }}>
        <h3 style={{ marginBottom: '16px' }}>📤 Import CSV Data</h3>
        <p style={{ marginBottom: '16px', opacity: 0.9 }}>Upload a CSV file to import historical tax data</p>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setImportFile(e.target.files?.[0] || null)}
            style={{
              padding: '8px 12px',
              borderRadius: '6px',
              border: '2px solid white',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              cursor: 'pointer'
            }}
          />
          <button
            onClick={handleImportCSV}
            disabled={!importFile || importing}
            className="btn btn-primary"
            style={{
              background: 'white',
              color: '#38a169',
              opacity: (!importFile || importing) ? 0.5 : 1,
              cursor: (!importFile || importing) ? 'not-allowed' : 'pointer'
            }}
          >
            {importing ? '⏳ Importing...' : '📥 Import CSV'}
          </button>
        </div>

        {importMessage && (
          <div style={{
            marginTop: '16px',
            padding: '12px',
            borderRadius: '6px',
            background: 'rgba(255,255,255,0.2)',
            fontWeight: 'bold'
          }}>
            {importMessage}
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Total Projects</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#667eea' }}>
            {summary.total_projects}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Total Revenue</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#48bb78' }}>
            {formatCurrency(summary.total_revenue)}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Total Tax Paid</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#e53e3e' }}>
            {formatCurrency(summary.total_tax_paid)}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Total Take Home</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#38a169' }}>
            {formatCurrency(summary.total_take_home)}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Avg Effective Rate</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#764ba2' }}>
            {summary.avg_effective_rate.toFixed(1)}%
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>Top Strategy</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#667eea', marginTop: '12px' }}>
            {summary.top_strategy}
          </div>
        </div>
      </div>

      {/* Strategy Effectiveness */}
      <div className="card">
        <h3 style={{ marginBottom: '24px' }}>🎯 Strategy Effectiveness</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>Strategy</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Projects</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Total Revenue</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Total Tax</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Avg Tax Rate</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Avg Take Home</th>
              </tr>
            </thead>
            <tbody>
              {strategies.map((strategy, idx) => (
                <tr key={idx} style={{
                  borderBottom: '1px solid #e2e8f0',
                  background: idx === 0 ? '#f0fff4' : idx === strategies.length - 1 ? '#fff5f5' : 'transparent'
                }}>
                  <td style={{ padding: '12px', fontWeight: 600 }}>
                    {idx === 0 && '🥇 '}
                    {idx === 1 && '🥈 '}
                    {idx === 2 && '🥉 '}
                    {strategy.strategy}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>{strategy.count}</td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>{formatCurrency(strategy.total_revenue)}</td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#e53e3e' }}>
                    {formatCurrency(strategy.total_tax)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', fontWeight: 'bold' }}>
                    {strategy.avg_effective_rate.toFixed(1)}%
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#38a169', fontWeight: 'bold' }}>
                    {formatCurrency(strategy.avg_take_home)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Insights */}
      <div className="card" style={{ marginTop: '24px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <h3 style={{ marginBottom: '16px' }}>💡 Key Insights</h3>
        <ul style={{ lineHeight: '2', paddingLeft: '20px' }}>
          <li>
            <strong>{summary.top_strategy}</strong> is your most used strategy ({summary.total_projects} projects)
          </li>
          <li>
            Average tax savings potential: <strong>{formatCurrency(summary.avg_project_revenue - summary.avg_tax_per_project)}</strong> per project
          </li>
          <li>
            Your overall effective tax rate is <strong>{summary.avg_effective_rate.toFixed(1)}%</strong>
          </li>
          {strategies.length > 0 && (
            <li>
              Best performing strategy: <strong>{strategies[0].strategy}</strong> with {strategies[0].avg_effective_rate.toFixed(1)}% tax rate
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Analytics;
