import React, { useState, useEffect } from 'react';
import { taxBracketsApi, TaxBracket, TaxBracketCreate } from '../api/client';

const TaxBracketsManagement: React.FC = () => {
  const [brackets, setBrackets] = useState<TaxBracket[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('US');
  const [selectedTaxType, setSelectedTaxType] = useState('Individual');
  const [showAddForm, setShowAddForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  // Form state
  const [newBracket, setNewBracket] = useState<TaxBracketCreate>({
    country: 'US',
    tax_type: 'Individual',
    income_limit: 0,
    rate: 0
  });

  useEffect(() => {
    loadBrackets();
  }, [selectedCountry, selectedTaxType]);

  const loadBrackets = async () => {
    setLoading(true);
    try {
      const response = await taxBracketsApi.getTaxBrackets(selectedCountry, selectedTaxType);
      setBrackets(response.data);
    } catch (error) {
      console.error('Error loading tax brackets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    try {
      await taxBracketsApi.createTaxBracket(newBracket);
      await loadBrackets();
      setShowAddForm(false);
      setNewBracket({
        country: selectedCountry,
        tax_type: selectedTaxType,
        income_limit: 0,
        rate: 0
      });
      alert('✅ Tax bracket added successfully!');
    } catch (error) {
      console.error('Error adding tax bracket:', error);
      alert('❌ Failed to add tax bracket');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await taxBracketsApi.deleteTaxBracket(id);
      setBrackets(brackets.filter(b => b.id !== id));
      setDeleteConfirm(null);
      alert('✅ Tax bracket deleted successfully!');
    } catch (error) {
      console.error('Error deleting tax bracket:', error);
      alert('❌ Failed to delete tax bracket');
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>💼 Tax Brackets Management</h2>
        <p>Manage tax brackets for different countries and tax types</p>
      </div>

      {/* Filter Controls */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div className="form-group">
            <label>🌍 Country</label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="form-control"
            >
              <option value="US">US</option>
              <option value="Spain">Spain</option>
            </select>
          </div>
          <div className="form-group">
            <label>📋 Tax Type</label>
            <select
              value={selectedTaxType}
              onChange={(e) => setSelectedTaxType(e.target.value)}
              className="form-control"
            >
              <option value="Individual">Individual</option>
              <option value="Business">Business</option>
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              onClick={() => {
                setNewBracket({
                  country: selectedCountry,
                  tax_type: selectedTaxType,
                  income_limit: 0,
                  rate: 0
                });
                setShowAddForm(true);
              }}
              className="btn-primary"
              style={{ width: '100%' }}
            >
              ➕ Add New Bracket
            </button>
          </div>
        </div>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="card" style={{ marginBottom: '24px', background: 'rgba(102, 126, 234, 0.08)' }}>
          <h3 style={{ marginBottom: '20px' }}>➕ Add Tax Bracket</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div className="form-group">
              <label>Income Limit ($)</label>
              <input
                type="number"
                value={newBracket.income_limit}
                onChange={(e) => setNewBracket({ ...newBracket, income_limit: parseFloat(e.target.value) })}
                className="form-control"
                step="0.01"
              />
            </div>
            <div className="form-group">
              <label>Tax Rate (%)</label>
              <input
                type="number"
                value={newBracket.rate * 100}
                onChange={(e) => setNewBracket({ ...newBracket, rate: parseFloat(e.target.value) / 100 })}
                className="form-control"
                step="0.01"
                min="0"
                max="100"
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button onClick={handleAdd} className="btn-primary">
              💾 Save Bracket
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="btn-secondary"
            >
              ✗ Cancel
            </button>
          </div>
        </div>
      )}

      {/* Brackets Table */}
      <div className="card">
        <h3 style={{ marginBottom: '24px' }}>
          📊 {selectedCountry} - {selectedTaxType} Tax Brackets ({brackets.length})
        </h3>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Income Limit</th>
                  <th>Tax Rate</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {brackets.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '40px', color: 'rgba(255, 255, 255, 0.5)' }}>
                      No tax brackets found for {selectedCountry} - {selectedTaxType}
                    </td>
                  </tr>
                ) : (
                  brackets.map((bracket) => (
                    <tr key={bracket.id}>
                      <td style={{ fontWeight: 700, color: '#667eea' }}>#{bracket.id}</td>
                      <td style={{ fontWeight: 600 }}>
                        ${bracket.income_limit.toLocaleString()}
                      </td>
                      <td>
                        <span style={{
                          padding: '6px 14px',
                          borderRadius: '8px',
                          fontSize: '14px',
                          fontWeight: 700,
                          background: bracket.rate < 0.15
                            ? 'rgba(16, 185, 129, 0.15)'
                            : bracket.rate < 0.25
                            ? 'rgba(251, 191, 36, 0.15)'
                            : 'rgba(239, 68, 68, 0.15)',
                          color: bracket.rate < 0.15
                            ? '#10b981'
                            : bracket.rate < 0.25
                            ? '#f59e0b'
                            : '#ef4444',
                          border: `2px solid ${bracket.rate < 0.15
                            ? 'rgba(16, 185, 129, 0.3)'
                            : bracket.rate < 0.25
                            ? 'rgba(251, 191, 36, 0.3)'
                            : 'rgba(239, 68, 68, 0.3)'}`
                        }}>
                          {(bracket.rate * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        {deleteConfirm === bracket.id ? (
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              onClick={() => handleDelete(bracket.id)}
                              className="btn-danger"
                              style={{ padding: '6px 12px', fontSize: '13px' }}
                            >
                              ✓ Confirm
                            </button>
                            <button
                              onClick={() => setDeleteConfirm(null)}
                              className="btn-secondary"
                              style={{ padding: '6px 12px', fontSize: '13px' }}
                            >
                              ✗ Cancel
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setDeleteConfirm(bracket.id)}
                            className="btn-danger"
                            style={{ padding: '6px 12px', fontSize: '13px' }}
                          >
                            🗑️ Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginTop: '24px' }}>
        <div className="stat-card">
          <h4>Total Brackets</h4>
          <div className="stat-value">{brackets.length}</div>
        </div>
        <div className="stat-card">
          <h4>Highest Rate</h4>
          <div className="stat-value">
            {brackets.length > 0 ? `${(Math.max(...brackets.map(b => b.rate)) * 100).toFixed(1)}%` : 'N/A'}
          </div>
        </div>
        <div className="stat-card">
          <h4>Lowest Rate</h4>
          <div className="stat-value">
            {brackets.length > 0 ? `${(Math.min(...brackets.map(b => b.rate)) * 100).toFixed(1)}%` : 'N/A'}
          </div>
        </div>
        <div className="stat-card">
          <h4>Max Income Limit</h4>
          <div className="stat-value">
            {brackets.length > 0 ? `$${Math.max(...brackets.map(b => b.income_limit)).toLocaleString()}` : 'N/A'}
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="card" style={{ marginTop: '24px', background: 'rgba(251, 191, 36, 0.08)' }}>
        <h4 style={{ marginBottom: '12px' }}>ℹ️ How Tax Brackets Work</h4>
        <ul style={{ fontSize: '14px', lineHeight: '1.8', color: 'rgba(255, 255, 255, 0.8)' }}>
          <li>Tax brackets define income thresholds and their corresponding tax rates</li>
          <li>The system calculates taxes progressively based on these brackets</li>
          <li>Each country and tax type (Individual/Business) has its own set of brackets</li>
          <li>Income limits are cumulative - income is taxed at different rates as it crosses each threshold</li>
          <li>Example: If you have brackets at $10k (10%) and $50k (20%), income from $0-$10k is taxed at 10%, and $10k-$50k at 20%</li>
        </ul>
      </div>
    </div>
  );
};

export default TaxBracketsManagement;
