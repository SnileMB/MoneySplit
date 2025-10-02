import React, { useEffect, useState } from 'react';
import { reportsApi, projectsApi, Statistics, Record } from '../api/client';

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
        <h2>Dashboard</h2>
        <p>Overview of your commission splitting business</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h4>Total Revenue</h4>
          <div className="stat-value">${stats?.total_revenue.toLocaleString() || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Total Projects</h4>
          <div className="stat-value">{stats?.total_records || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Tax Paid</h4>
          <div className="stat-value">${stats?.total_tax.toLocaleString() || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Net Income</h4>
          <div className="stat-value">${stats?.total_net_income.toLocaleString() || 0}</div>
        </div>
      </div>

      <div className="card">
        <h3>Recent Projects</h3>
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
                <td>#{record.id}</td>
                <td>{new Date(record.created_at).toLocaleDateString()}</td>
                <td>{record.tax_origin}</td>
                <td>{record.tax_option}</td>
                <td>${record.revenue.toLocaleString()}</td>
                <td>${record.net_income_group.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h4>Average Tax Rate</h4>
          <div className="stat-value">{stats?.average_tax_rate.toFixed(1)}%</div>
        </div>
        <div className="stat-card">
          <h4>Unique People</h4>
          <div className="stat-value">{stats?.unique_people || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Total Costs</h4>
          <div className="stat-value">${stats?.total_costs.toLocaleString() || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Profit Margin</h4>
          <div className="stat-value">
            {stats
              ? ((stats.total_net_income / stats.total_revenue) * 100).toFixed(1)
              : 0}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
