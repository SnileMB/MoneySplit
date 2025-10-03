import React, { useState } from 'react';
import { projectsApi, ProjectCreate, Person } from '../api/client';

const Projects: React.FC = () => {
  const [numPeople, setNumPeople] = useState<number>(2);
  const [revenue, setRevenue] = useState<string>('');
  const [costs, setCosts] = useState<string>('');
  const [country, setCountry] = useState<string>('US');
  const [taxType, setTaxType] = useState<'Individual' | 'Business'>('Individual');
  const [people, setPeople] = useState<Person[]>([
    { name: '', work_share: 0.5 },
    { name: '', work_share: 0.5 },
  ]);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [loading, setLoading] = useState(false);

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
    </div>
  );
};

export default Projects;
