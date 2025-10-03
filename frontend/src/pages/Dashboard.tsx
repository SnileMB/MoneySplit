import React, { useEffect, useState } from 'react';
import { reportsApi, projectsApi, Statistics, Record } from '../api/client';

// Format dollar amounts - round down to nearest dollar
const formatCurrency = (amount: number): string => {
  return Math.floor(amount).toLocaleString();
};

// Determine font size based on string length
const getValueLength = (value: string | number): string => {
  const strValue = String(value);
  if (strValue.length > 10) return 'very-long';
  if (strValue.length > 7) return 'long';
  return 'normal';
};

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [recentRecords, setRecentRecords] = useState<Record[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, recordsRes] = await Promise.all([
          reportsApi.getStatistics(),
          projectsApi.getRecords(5),
        ]);
        setStats(statsRes.data);
        setRecentRecords(recordsRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h2>📊 Dashboard</h2>
        <p>Overview of your commission splitting business</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>💰</div>
          <h4>Total Revenue</h4>
          <div className="stat-value" data-length={stats ? getValueLength(`$${formatCurrency(stats.total_revenue)}`) : 'normal'}>
            ${stats ? formatCurrency(stats.total_revenue) : 0}
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            All time earnings
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>📁</div>
          <h4>Total Projects</h4>
          <div className="stat-value" data-length={getValueLength(stats?.total_records || 0)}>
            {stats?.total_records || 0}
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Completed projects
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>🏛️</div>
          <h4>Tax Paid</h4>
          <div className="stat-value" data-length={stats ? getValueLength(`$${formatCurrency(stats.total_tax)}`) : 'normal'}>
            ${stats ? formatCurrency(stats.total_tax) : 0}
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Total contributions
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>✨</div>
          <h4>Net Income</h4>
          <div className="stat-value" data-length={stats ? getValueLength(`$${formatCurrency(stats.total_net_income)}`) : 'normal'}>
            ${stats ? formatCurrency(stats.total_net_income) : 0}
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            After tax profits
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '24px' }}>🕐 Recent Projects</h3>
        {recentRecords.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Date</th>
                  <th>Country</th>
                  <th>Tax Type</th>
                  <th>Revenue</th>
                  <th>Net Income</th>
                </tr>
              </thead>
              <tbody>
                {recentRecords.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <span style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: 600
                      }}>
                        #{record.id}
                      </span>
                    </td>
                    <td>{new Date(record.created_at).toLocaleDateString()}</td>
                    <td>
                      <span style={{ fontWeight: 600 }}>{record.tax_origin}</span>
                    </td>
                    <td>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '8px',
                        fontSize: '13px',
                        fontWeight: 500,
                        background: record.tax_option === 'Individual'
                          ? 'rgba(102, 126, 234, 0.1)'
                          : 'rgba(118, 75, 162, 0.1)',
                        color: record.tax_option === 'Individual'
                          ? '#667eea'
                          : '#764ba2'
                      }}>
                        {record.tax_option}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, color: '#2d3748' }}>
                      ${formatCurrency(record.revenue)}
                    </td>
                    <td style={{
                      fontWeight: 700,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      ${formatCurrency(record.net_income_group)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '48px 24px',
            color: '#718096'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>📭</div>
            <p style={{ fontSize: '18px', fontWeight: 500 }}>No projects yet</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>Create your first project to get started!</p>
          </div>
        )}
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>📊</div>
          <h4>Average Tax Rate</h4>
          <div className="stat-value">{stats?.average_tax_rate.toFixed(1)}%</div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Effective rate
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>👥</div>
          <h4>Unique People</h4>
          <div className="stat-value">{stats?.unique_people || 0}</div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Team members
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>💸</div>
          <h4>Total Costs</h4>
          <div className="stat-value" data-length={stats ? getValueLength(`$${formatCurrency(stats.total_costs)}`) : 'normal'}>
            ${stats ? formatCurrency(stats.total_costs) : 0}
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Business expenses
          </div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: '36px', marginBottom: '8px' }}>📈</div>
          <h4>Profit Margin</h4>
          <div className="stat-value" data-length="normal">
            {stats
              ? Math.floor((stats.total_net_income / stats.total_revenue) * 100)
              : 0}%
          </div>
          <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontWeight: 500 }}>
            Net profit ratio
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
