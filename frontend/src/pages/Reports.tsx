import React, { useState, useEffect } from 'react';
import { forecastApi, exportApi, visualizationApi, Forecast } from '../api/client';

const Reports: React.FC = () => {
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadForecast();
  }, []);

  const loadForecast = async () => {
    setLoading(true);
    try {
      const response = await forecastApi.getRevenueForecast(3);
      setForecast(response.data);
    } catch (error) {
      console.error('Error loading forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Reports & Analytics</h2>
        <p>Visualizations, forecasts, and export options</p>
      </div>

      <div className="card">
        <h3>📊 Interactive Visualizations</h3>
        <p style={{ marginBottom: '16px', color: '#7f8c8d' }}>
          Click any visualization to open it in a new tab
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <button
            className="btn btn-primary"
            onClick={() => window.open(visualizationApi.getRevenueSummary(), '_blank')}
          >
            📈 Revenue Summary
          </button>
          <button
            className="btn btn-primary"
            onClick={() => window.open(visualizationApi.getMonthlyTrends(), '_blank')}
          >
            📅 Monthly Trends
          </button>
          <button
            className="btn btn-primary"
            onClick={() => window.open(visualizationApi.getWorkDistribution(), '_blank')}
          >
            🥧 Work Distribution
          </button>
          <button
            className="btn btn-primary"
            onClick={() => window.open(visualizationApi.getTaxComparison(), '_blank')}
          >
            💰 Tax Comparison
          </button>
          <button
            className="btn btn-primary"
            onClick={() => window.open(visualizationApi.getProjectProfitability(), '_blank')}
          >
            💵 Profitability
          </button>
        </div>
      </div>

      <div className="card">
        <h3>🔮 Revenue Forecast</h3>
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : forecast?.success ? (
          <>
            <div style={{ marginBottom: '20px' }}>
              <p><strong>Trend:</strong> {forecast.trend} (${forecast.trend_strength.toFixed(0)}/month)</p>
              <p><strong>Confidence:</strong> {forecast.confidence} (R² = {forecast.r2_score.toFixed(2)})</p>
              <p><strong>Historical Average:</strong> ${forecast.historical_avg.toLocaleString()}</p>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Predicted Revenue</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {forecast.predictions.map((pred) => (
                  <tr key={pred.month}>
                    <td>{pred.month}</td>
                    <td>${pred.revenue.toLocaleString()}</td>
                    <td>{pred.confidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        ) : (
          <p>Not enough data for forecasting. Create at least 2 projects.</p>
        )}
      </div>

      <div className="card">
        <h3>📄 PDF Exports</h3>
        <p style={{ marginBottom: '16px', color: '#7f8c8d' }}>
          Download professional PDF reports
        </p>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <a
            href={exportApi.exportSummaryPDF()}
            download
            className="btn btn-success"
          >
            Download Summary Report
          </a>
          <a
            href={exportApi.exportForecastPDF()}
            download
            className="btn btn-success"
          >
            Download Forecast Report
          </a>
        </div>
      </div>
    </div>
  );
};

export default Reports;
