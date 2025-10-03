import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Strategy {
  strategy_name: string;
  gross_income: number;
  total_tax: number;
  net_income_group: number;
  net_income_per_person: number;
  effective_rate: number;
  breakdown: Array<{ label: string; amount: number; note?: string }>;
  corporate_tax?: number;
  personal_tax?: number;
  se_tax?: number;
  dividend_tax?: number;
  standard_deduction_used?: number;
  company_retained?: number;
}

interface OptimalResult {
  all_strategies: Strategy[];
  optimal: Strategy;
  worst: Strategy;
  savings: number;
}

interface TaxCalculatorProps {
  onCreateProject?: (data: {
    revenue: number;
    costs: number;
    numPeople: number;
    country: string;
    taxType: 'Individual' | 'Business';
    distributionMethod: string;
  }) => void;
}

const TaxCalculator: React.FC<TaxCalculatorProps> = ({ onCreateProject }) => {
  const [revenue, setRevenue] = useState<string>('100000');
  const [costs, setCosts] = useState<string>('20000');
  const [numPeople, setNumPeople] = useState<number>(2);
  const [country, setCountry] = useState<string>('US');
  const [state, setState] = useState<string>('');
  const [result, setResult] = useState<OptimalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Auto-calculate on input change
  useEffect(() => {
    const calculateStrategies = async () => {
      if (!revenue || !costs || !country) return;

      const revenueNum = parseFloat(revenue);
      const costsNum = parseFloat(costs);

      if (isNaN(revenueNum) || isNaN(costsNum) || revenueNum <= 0) return;

      setLoading(true);
      setError('');

      try {
        const params: any = {
          revenue: revenueNum,
          costs: costsNum,
          num_people: numPeople,
          country: country,
        };

        // Add state parameter if US and state is selected
        if (country === 'US' && state) {
          params.state = state;
        }

        const response = await axios.get<OptimalResult>('http://localhost:8000/api/optimal-strategy', {
          params
        });
        setResult(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error calculating strategies');
        setResult(null);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(calculateStrategies, 500);
    return () => clearTimeout(timeoutId);
  }, [revenue, costs, numPeople, country, state]);

  const formatCurrency = (amount: number): string => {
    return Math.floor(amount).toLocaleString();
  };

  const getStrategyIcon = (name: string): string => {
    if (name.includes('Individual')) return '👤';
    if (name.includes('Dividend')) return '💰';
    if (name.includes('Mixed')) return '🎯';
    if (name.includes('Salary')) return '💼';
    if (name.includes('Reinvest')) return '🌱';
    return '📊';
  };

  const handleCreateProject = (strategy: Strategy) => {
    if (!onCreateProject) return;

    // Determine tax type and distribution method from strategy name
    let taxType: 'Individual' | 'Business' = 'Individual';
    let distributionMethod = 'N/A';

    if (strategy.strategy_name.includes('Business')) {
      taxType = 'Business';
      if (strategy.strategy_name.includes('Salary')) {
        distributionMethod = 'Salary';
      } else if (strategy.strategy_name.includes('Dividend')) {
        distributionMethod = 'Dividend';
      } else if (strategy.strategy_name.includes('Mixed')) {
        distributionMethod = 'Mixed';
      } else if (strategy.strategy_name.includes('Reinvest')) {
        distributionMethod = 'Reinvest';
      }
    }

    onCreateProject({
      revenue: parseFloat(revenue),
      costs: parseFloat(costs),
      numPeople: numPeople,
      country: country,
      taxType: taxType,
      distributionMethod: distributionMethod
    });
  };


  return (
    <div>
      <div className="page-header">
        <h2>💡 Tax Strategy Calculator</h2>
        <p>Find the optimal tax approach to maximize your take-home income</p>
      </div>

      {/* Input Form */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ marginBottom: '24px' }}>📋 Enter Your Project Details</h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Revenue ($)
              <span style={{ cursor: 'help', fontSize: '14px' }} title="Total project revenue before any deductions">ℹ️</span>
            </label>
            <input
              type="number"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              placeholder="100000"
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Total Costs ($)
              <span style={{ cursor: 'help', fontSize: '14px' }} title="Business expenses, materials, overhead costs">ℹ️</span>
            </label>
            <input
              type="number"
              value={costs}
              onChange={(e) => setCosts(e.target.value)}
              placeholder="20000"
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Number of People
              <span style={{ cursor: 'help', fontSize: '14px' }} title="Team members sharing this project income">ℹ️</span>
            </label>
            <input
              type="number"
              min="1"
              value={numPeople}
              onChange={(e) => setNumPeople(parseInt(e.target.value))}
            />
          </div>

          <div className="form-group">
            <label>Country</label>
            <select value={country} onChange={(e) => { setCountry(e.target.value); setState(''); }}>
              <option value="US">United States</option>
              <option value="Spain">Spain</option>
              <option value="UK">United Kingdom</option>
              <option value="Canada">Canada</option>
            </select>
          </div>

          {country === 'US' && (
            <div className="form-group">
              <label>State (Optional)</label>
              <select value={state} onChange={(e) => setState(e.target.value)}>
                <option value="">None</option>
                <option value="CA">California</option>
                <option value="NY">New York</option>
                <option value="TX">Texas</option>
                <option value="FL">Florida</option>
              </select>
            </div>
          )}
        </div>

        <div style={{ marginTop: '16px', padding: '12px', background: '#f7fafc', borderRadius: '8px' }}>
          <strong>Gross Income: </strong>
          ${formatCurrency(parseFloat(revenue || '0') - parseFloat(costs || '0'))}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <p>Calculating optimal tax strategies...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="alert alert-error">
          <span style={{ fontSize: '24px', marginRight: '12px' }}>❌</span>
          {error}
        </div>
      )}

      {/* Results */}
      {!loading && !error && result && (
        <>
          {/* Recommendation Banner */}
          <div className="alert" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            marginBottom: '32px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ fontSize: '64px' }}>🏆</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                  Best Strategy: {result.optimal.strategy_name}
                </div>
                <div style={{ fontSize: '18px', opacity: 0.95, marginBottom: '8px' }}>
                  Take Home: <strong>${formatCurrency(result.optimal.net_income_group)}</strong>
                  {' '}(${formatCurrency(result.optimal.net_income_per_person)} per person)
                </div>
                {result.savings > 0 && (
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    💰 Save <strong>${formatCurrency(result.savings)}</strong> compared to worst strategy
                    {' '}({((result.savings / result.worst.net_income_group) * 100).toFixed(1)}% more money!)
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Strategy Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
          }}>
            {result.all_strategies
              .filter(s => s.net_income_group > 0) // Hide Reinvest for now
              .sort((a, b) => b.net_income_group - a.net_income_group)
              .map((strategy, index) => (
                <StrategyCard
                  key={index}
                  strategy={strategy}
                  isOptimal={strategy === result.optimal}
                  rank={index + 1}
                  formatCurrency={formatCurrency}
                  getStrategyIcon={getStrategyIcon}
                  onCreateProject={() => handleCreateProject(strategy)}
                />
              ))}
          </div>

          {/* Comparison Chart */}
          <div className="card">
            <h3 style={{ marginBottom: '24px' }}>📊 Visual Comparison</h3>
            <ComparisonChart
              strategies={result.all_strategies.filter(s => s.net_income_group > 0)}
              formatCurrency={formatCurrency}
            />
          </div>
        </>
      )}
    </div>
  );
};

// Strategy Card Component
const StrategyCard: React.FC<{
  strategy: Strategy;
  isOptimal: boolean;
  rank: number;
  formatCurrency: (n: number) => string;
  getStrategyIcon: (name: string) => string;
  onCreateProject?: () => void;
}> = ({ strategy, isOptimal, rank, formatCurrency, getStrategyIcon, onCreateProject }) => {
  const rankEmoji = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '  ';

  // Favorite strategies (localStorage)
  const [isFavorite, setIsFavorite] = React.useState(() => {
    const favorites = JSON.parse(localStorage.getItem('favoriteStrategies') || '[]');
    return favorites.includes(strategy.strategy_name);
  });

  const toggleFavorite = () => {
    const favorites = JSON.parse(localStorage.getItem('favoriteStrategies') || '[]');
    if (isFavorite) {
      const updated = favorites.filter((f: string) => f !== strategy.strategy_name);
      localStorage.setItem('favoriteStrategies', JSON.stringify(updated));
    } else {
      favorites.push(strategy.strategy_name);
      localStorage.setItem('favoriteStrategies', JSON.stringify(favorites));
    }
    setIsFavorite(!isFavorite);
  };

  return (
    <div className="card" style={{
      border: isOptimal ? '3px solid #48bb78' : undefined,
      background: isOptimal ? '#f0fff4' : undefined,
      position: 'relative'
    }}>
      {isOptimal && (
        <div style={{
          position: 'absolute',
          top: '-12px',
          right: '16px',
          background: '#48bb78',
          color: 'white',
          padding: '6px 16px',
          borderRadius: '16px',
          fontSize: '13px',
          fontWeight: 'bold'
        }}>
          ⭐ BEST OPTION
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <span style={{ fontSize: '32px' }}>{rankEmoji}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '4px' }}>
            {getStrategyIcon(strategy.strategy_name)}
          </div>
          <h3 style={{ margin: 0, fontSize: '18px' }}>{strategy.strategy_name}</h3>
        </div>
        <button
          onClick={toggleFavorite}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            padding: '4px',
            transition: 'transform 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.2)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {isFavorite ? '⭐' : '☆'}
        </button>
      </div>

      {/* Main Metric */}
      <div style={{
        background: '#f7fafc',
        padding: '20px',
        borderRadius: '12px',
        marginBottom: '16px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '14px', color: '#718096', marginBottom: '8px' }}>
          Take Home (Total)
        </div>
        <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2d3748' }}>
          ${formatCurrency(strategy.net_income_group)}
        </div>
        <div style={{ fontSize: '14px', color: '#718096', marginTop: '8px' }}>
          ${formatCurrency(strategy.net_income_per_person)} per person
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <div>
          <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Total Tax</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#e53e3e' }}>
            ${formatCurrency(strategy.total_tax)}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Effective Rate</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#718096' }}>
            {strategy.effective_rate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Tax Breakdown */}
      <details style={{ marginTop: '16px' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 600, marginBottom: '12px' }}>
          📋 Tax Breakdown
        </summary>
        {strategy.breakdown.map((item, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px',
            fontSize: '14px',
            paddingLeft: '16px'
          }}>
            <span style={{ color: '#718096' }}>
              {item.label}
              {item.note && <div style={{ fontSize: '12px', fontStyle: 'italic', color: '#a0aec0' }}>{item.note}</div>}
            </span>
            <span style={{ fontWeight: 600 }}>${formatCurrency(item.amount)}</span>
          </div>
        ))}
      </details>

      {/* Create Project Button */}
      {onCreateProject && (
        <button
          className="btn btn-primary"
          onClick={onCreateProject}
          style={{
            width: '100%',
            marginTop: '20px',
            background: isOptimal
              ? 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: 600
          }}
        >
          {isOptimal ? '🚀 Create Project with Best Strategy' : '📝 Create Project with This Strategy'}
        </button>
      )}
    </div>
  );
};

// Comparison Chart Component
const ComparisonChart: React.FC<{
  strategies: Strategy[];
  formatCurrency: (n: number) => string;
}> = ({ strategies, formatCurrency }) => {
  const maxTakeHome = Math.max(...strategies.map(s => s.net_income_group));

  return (
    <div>
      {strategies
        .sort((a, b) => b.net_income_group - a.net_income_group)
        .map((strategy, idx) => {
          const percentage = (strategy.net_income_group / maxTakeHome) * 100;

          return (
            <div key={idx} style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, fontSize: '14px' }}>{strategy.strategy_name}</span>
                <span style={{ fontWeight: 700, fontSize: '14px' }}>
                  ${formatCurrency(strategy.net_income_group)}
                </span>
              </div>
              <div style={{
                width: '100%',
                height: '32px',
                background: '#e2e8f0',
                borderRadius: '8px',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <div style={{
                  width: `${percentage}%`,
                  height: '100%',
                  background: idx === 0
                    ? 'linear-gradient(90deg, #48bb78 0%, #38a169 100%)'
                    : 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  transition: 'width 0.3s ease'
                }}></div>
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  right: '12px',
                  transform: 'translateY(-50%)',
                  fontSize: '13px',
                  fontWeight: 'bold',
                  color: percentage > 50 ? 'white' : '#2d3748'
                }}>
                  {strategy.effective_rate.toFixed(1)}% tax
                </div>
              </div>
            </div>
          );
        })}
    </div>
  );
};

export default TaxCalculator;
