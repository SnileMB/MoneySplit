import React, { useState, useEffect } from 'react';
import { projectsApi, ProjectCreate, Person } from '../api/client';
import axios from 'axios';

interface TaxScenario {
  type: string;
  description: string;
  gross_income: number;
  tax_paid?: number;
  corporate_tax?: number;
  personal_tax?: number;
  dividend_tax?: number;
  total_tax: number;
  take_home_per_person: number;
  take_home_total: number;
  effective_rate: number;
  tax_breakdown: Array<{ label: string; amount: number; note?: string }>;
  company_retained?: number;
  note?: string;
}

interface TaxComparison {
  individual: TaxScenario;
  business_salary: TaxScenario;
  business_dividend: TaxScenario;
  business_reinvest: TaxScenario;
  recommendation: {
    choice: string;
    reason: string;
    savings: number;
    warning: string | null;
  };
}

interface ProjectsProps {
  prefilledData?: {
    revenue: number;
    costs: number;
    numPeople: number;
    country: string;
    taxType: 'Individual' | 'Business';
    distributionMethod: string;
  } | null;
}

const Projects: React.FC<ProjectsProps> = ({ prefilledData }) => {
  const [numPeople, setNumPeople] = useState<number>(prefilledData?.numPeople || 2);
  const [revenue, setRevenue] = useState<string>(prefilledData?.revenue.toString() || '');
  const [costs, setCosts] = useState<string>(prefilledData?.costs.toString() || '');
  const [country, setCountry] = useState<string>(prefilledData?.country || 'US');
  const [taxType, setTaxType] = useState<'Individual' | 'Business'>(prefilledData?.taxType || 'Individual');
  const [people, setPeople] = useState<Person[]>(
    Array.from({ length: prefilledData?.numPeople || 2 }, (_, i) => ({
      name: '',
      work_share: 1 / (prefilledData?.numPeople || 2)
    }))
  );
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [taxComparison, setTaxComparison] = useState<TaxComparison | null>(null);
  const [loadingComparison, setLoadingComparison] = useState(false);

  const handleNumPeopleChange = (value: number) => {
    setNumPeople(value);
    const newPeople: Person[] = [];
    const sharePerPerson = 1 / value;

    for (let i = 0; i < value; i++) {
      newPeople.push({
        name: people[i]?.name || '',
        work_share: sharePerPerson,
      });
    }
    setPeople(newPeople);
  };

  const handlePersonChange = (index: number, field: keyof Person, value: string | number) => {
    const newPeople = [...people];
    newPeople[index] = { ...newPeople[index], [field]: value };
    setPeople(newPeople);
  };

  // Fetch tax comparison when revenue, costs, numPeople, or country changes
  useEffect(() => {
    const fetchTaxComparison = async () => {
      if (!revenue || !costs || !country || (country !== 'US' && country !== 'Spain')) {
        setTaxComparison(null);
        return;
      }

      try {
        const costsArray = costs.split(',').map(c => parseFloat(c.trim()));
        const totalCosts = costsArray.reduce((sum, c) => sum + c, 0);

        if (isNaN(parseFloat(revenue)) || isNaN(totalCosts)) {
          setTaxComparison(null);
          return;
        }

        setLoadingComparison(true);
        const response = await axios.get<TaxComparison>('http://localhost:8000/api/tax-comparison', {
          params: {
            revenue: parseFloat(revenue),
            costs: totalCosts,
            num_people: numPeople,
            country: country,
          },
        });
        setTaxComparison(response.data);
      } catch (error) {
        console.error('Error fetching tax comparison:', error);
        setTaxComparison(null);
      } finally {
        setLoadingComparison(false);
      }
    };

    // Debounce the API call
    const timeoutId = setTimeout(fetchTaxComparison, 500);
    return () => clearTimeout(timeoutId);
  }, [revenue, costs, numPeople, country]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');
    setLoading(true);

    try {
      const costsArray = costs.split(',').map(c => parseFloat(c.trim()));

      const data: ProjectCreate = {
        num_people: numPeople,
        revenue: parseFloat(revenue),
        costs: costsArray,
        country,
        tax_type: taxType,
        people,
      };

      const response = await projectsApi.create(data);
      setSuccessMessage(`Project created successfully! Record ID: ${response.data.record_id}`);

      // Reset form
      setRevenue('');
      setCosts('');
      handleNumPeopleChange(2);
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Error creating project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>✨ New Project</h2>
        <p>Create a new commission splitting project</p>
      </div>

      {prefilledData && (
        <div className="alert" style={{
          background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
          color: 'white',
          border: 'none',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ fontSize: '48px' }}>✅</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '8px' }}>
                Pre-filled with Optimal Strategy
              </div>
              <div style={{ fontSize: '16px', opacity: 0.95 }}>
                Using <strong>{prefilledData.taxType}</strong> tax
                {prefilledData.distributionMethod !== 'N/A' && ` with ${prefilledData.distributionMethod} distribution`}
                {' '}for ${prefilledData.revenue.toLocaleString()} revenue project
              </div>
              <div style={{ fontSize: '14px', marginTop: '8px', opacity: 0.9 }}>
                Just add team member names below and create your project!
              </div>
            </div>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '24px' }}>✅</span>
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="alert alert-error" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '24px' }}>❌</span>
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Number of People</label>
            <input
              type="number"
              min="1"
              value={numPeople}
              onChange={(e) => handleNumPeopleChange(parseInt(e.target.value))}
              required
            />
          </div>

          <div className="form-group">
            <label>Revenue ($)</label>
            <input
              type="number"
              step="0.01"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              placeholder="10000"
              required
            />
          </div>

          <div className="form-group">
            <label>Costs (comma-separated)</label>
            <input
              type="text"
              value={costs}
              onChange={(e) => setCosts(e.target.value)}
              placeholder="1000, 500, 300"
              required
            />
          </div>

          <div className="form-group">
            <label>Country</label>
            <select value={country} onChange={(e) => setCountry(e.target.value)}>
              <option value="US">United States</option>
              <option value="Spain">Spain</option>
              <option value="UK">United Kingdom</option>
              <option value="Canada">Canada</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label>Tax Type</label>
            <select value={taxType} onChange={(e) => setTaxType(e.target.value as 'Individual' | 'Business')}>
              <option value="Individual">Individual</option>
              <option value="Business">Business</option>
            </select>
          </div>

          <h3 style={{ marginTop: '32px', marginBottom: '20px' }}>👥 Team Members</h3>
          {people.map((person, index) => (
            <div key={index} className="person-card">
              <div className="form-group">
                <label>Person {index + 1} - Name</label>
                <input
                  type="text"
                  value={person.name}
                  onChange={(e) => handlePersonChange(index, 'name', e.target.value)}
                  placeholder="John Doe"
                  required
                />
              </div>
              <div className="form-group">
                <label>Work Share (0 - 1)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={person.work_share}
                  onChange={(e) => handlePersonChange(index, 'work_share', parseFloat(e.target.value))}
                  required
                />
                <small style={{ display: 'block', marginTop: '8px', color: '#718096', fontWeight: 500 }}>
                  {(person.work_share * 100).toFixed(0)}% of total work
                </small>
              </div>
            </div>
          ))}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      </div>

      {/* Tax Comparison Section */}
      {(country === 'US' || country === 'Spain') && revenue && costs && (
        <div style={{ marginTop: '32px' }}>
          <div className="page-header">
            <h2>💡 Tax Strategy Comparison</h2>
            <p>See which tax approach saves you the most money</p>
          </div>

          {loadingComparison && (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
              <p>Calculating tax scenarios...</p>
            </div>
          )}

          {!loadingComparison && taxComparison && (
            <>
              {/* Recommendation Banner */}
              <div className="alert" style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                marginBottom: '24px'
              }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '8px' }}>
                  🎯 Best Choice: {taxComparison.recommendation.choice}
                </div>
                <div style={{ fontSize: '16px', opacity: 0.95 }}>
                  {taxComparison.recommendation.reason}
                </div>
                {taxComparison.recommendation.warning && (
                  <div style={{ marginTop: '12px', fontSize: '14px', opacity: 0.9 }}>
                    {taxComparison.recommendation.warning}
                  </div>
                )}
              </div>

              {/* Scenario Cards */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '20px',
                marginBottom: '32px'
              }}>
                {/* Individual */}
                <TaxScenarioCard
                  scenario={taxComparison.individual}
                  isRecommended={taxComparison.recommendation.choice === 'Individual Tax'}
                  isSelected={taxType === 'Individual'}
                />

                {/* Business - Dividend */}
                <TaxScenarioCard
                  scenario={taxComparison.business_dividend}
                  isRecommended={taxComparison.recommendation.choice === 'Business Tax with Dividend Distribution'}
                  isSelected={taxType === 'Business'}
                />

                {/* Business - Salary */}
                <TaxScenarioCard
                  scenario={taxComparison.business_salary}
                  isRecommended={taxComparison.recommendation.choice === 'Business Tax with Salary'}
                  isSelected={taxType === 'Business'}
                />

                {/* Business - Reinvest */}
                <TaxScenarioCard
                  scenario={taxComparison.business_reinvest}
                  isRecommended={false}
                  isSelected={false}
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

// Tax Scenario Card Component
const TaxScenarioCard: React.FC<{
  scenario: TaxScenario;
  isRecommended: boolean;
  isSelected: boolean;
}> = ({ scenario, isRecommended, isSelected }) => {
  return (
    <div className="card" style={{
      border: isRecommended ? '3px solid #48bb78' : isSelected ? '2px solid #4299e1' : undefined,
      position: 'relative',
      background: isRecommended ? '#f0fff4' : undefined
    }}>
      {isRecommended && (
        <div style={{
          position: 'absolute',
          top: '-12px',
          right: '16px',
          background: '#48bb78',
          color: 'white',
          padding: '4px 12px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          ⭐ BEST OPTION
        </div>
      )}
      {isSelected && !isRecommended && (
        <div style={{
          position: 'absolute',
          top: '-12px',
          right: '16px',
          background: '#4299e1',
          color: 'white',
          padding: '4px 12px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          YOUR SELECTION
        </div>
      )}

      <h3 style={{ marginBottom: '8px', fontSize: '18px' }}>{scenario.type}</h3>
      <p style={{ color: '#718096', fontSize: '14px', marginBottom: '20px' }}>
        {scenario.description}
      </p>

      {/* Key Metrics */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          background: '#f7fafc',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '12px'
        }}>
          <div style={{ fontSize: '14px', color: '#718096', marginBottom: '4px' }}>
            Take Home Per Person
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2d3748' }}>
            ${scenario.take_home_per_person.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>
              Total Tax
            </div>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#e53e3e' }}>
              ${scenario.total_tax.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>
              Effective Rate
            </div>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#718096' }}>
              {scenario.effective_rate.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Tax Breakdown */}
      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
        <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: '#2d3748' }}>
          Tax Breakdown:
        </div>
        {scenario.tax_breakdown.map((item, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px',
            fontSize: '14px'
          }}>
            <span style={{ color: '#718096' }}>{item.label}</span>
            <span style={{ fontWeight: 600, color: '#2d3748' }}>
              ${item.amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </span>
          </div>
        ))}
        {scenario.company_retained !== undefined && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            background: '#edf2f7',
            borderRadius: '6px'
          }}>
            <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>
              Company Retained
            </div>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748' }}>
              ${scenario.company_retained.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </div>
            {scenario.note && (
              <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', fontStyle: 'italic' }}>
                {scenario.note}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;
