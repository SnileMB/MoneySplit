import React, { useState, useEffect } from "react";
import { projectsApi } from "../api/client";

interface Record {
  id: number;
  num_people: number;
  revenue: number;
  total_costs: number;
  group_income: number;
  individual_income: number;
  tax_origin: string;
  tax_option: string;
  tax_amount: number;
  net_income_per_person: number;
  net_income_group: number;
  created_at: string;
}

const RecordsManagement: React.FC = () => {
  const [records, setRecords] = useState<Record[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCountry, setFilterCountry] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [editingRecord, setEditingRecord] = useState<number | null>(null);
  const [editField, setEditField] = useState("");
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const response = await projectsApi.getRecords(100); // Get more records
      setRecords(response.data);
    } catch (error) {
      console.error("Error loading records:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await projectsApi.deleteRecord(id);
      setRecords(records.filter(r => r.id !== id));
      setDeleteConfirm(null);
      alert("✅ Record deleted successfully!");
    } catch (error) {
      console.error("Error deleting record:", error);
      alert("❌ Failed to delete record");
    }
  };

  const handleEditClick = (record: Record, field: string) => {
    setEditingRecord(record.id);
    setEditField(field);
    const value = (record as unknown as { [key: string]: unknown })[field];
    setEditValue(String(value));
  };

  const handleEditSave = async () => {
    if (!editingRecord || !editField) {
      return;
    }

    try {
      const value = ["num_people", "revenue", "total_costs"].includes(editField)
        ? parseFloat(editValue)
        : editValue;

      await projectsApi.updateRecord(editingRecord, { field: editField, value });

      // Reload records to get recalculated values
      await loadRecords();

      setEditingRecord(null);
      setEditField("");
      setEditValue("");
      alert("✅ Record updated successfully!");
    } catch (error) {
      console.error("Error updating record:", error);
      alert("❌ Failed to update record");
    }
  };

  const cancelEdit = () => {
    setEditingRecord(null);
    setEditField("");
    setEditValue("");
  };

  const filteredRecords = records.filter(record => {
    const matchesSearch = searchTerm === "" ||
      record.id.toString().includes(searchTerm) ||
      record.tax_origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.tax_option.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCountry = filterCountry === "" || record.tax_origin === filterCountry;

    return matchesSearch && matchesCountry;
  });

  const countries = Array.from(new Set(records.map(r => r.tax_origin)));

  return (
    <div>
      <div className="page-header">
        <h2>📋 Records Management</h2>
        <p>View, edit, and delete project records</p>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: "24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "16px" }}>
          <div className="form-group">
            <label>🔍 Search by ID, Country, or Tax Type</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search..."
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>🌍 Filter by Country</label>
            <select
              value={filterCountry}
              onChange={(e) => setFilterCountry(e.target.value)}
              className="form-control"
            >
              <option value="">All Countries</option>
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Records Table */}
      <div className="card">
        <h3 style={{ marginBottom: "24px" }}>
          📊 All Records ({filteredRecords.length})
        </h3>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Date</th>
                  <th>Country</th>
                  <th>Tax Type</th>
                  <th>People</th>
                  <th>Revenue</th>
                  <th>Costs</th>
                  <th>Net Income</th>
                  <th>Tax Paid</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.length === 0 ? (
                  <tr>
                    <td colSpan={10} style={{ textAlign: "center", padding: "40px", color: "rgba(255, 255, 255, 0.5)" }}>
                      No records found
                    </td>
                  </tr>
                ) : (
                  filteredRecords.map((record) => (
                    <tr key={record.id}>
                      <td style={{ fontWeight: 700, color: "#667eea" }}>#{record.id}</td>
                      <td>{new Date(record.created_at).toLocaleDateString()}</td>
                      <td>
                        <span style={{
                          padding: "4px 12px",
                          borderRadius: "8px",
                          background: "rgba(102, 126, 234, 0.15)",
                          border: "1px solid rgba(102, 126, 234, 0.3)",
                          fontSize: "13px",
                          fontWeight: 600,
                        }}>
                          {record.tax_origin}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          padding: "4px 12px",
                          borderRadius: "8px",
                          background: record.tax_option === "Individual"
                            ? "rgba(16, 185, 129, 0.15)"
                            : "rgba(240, 147, 251, 0.15)",
                          border: `1px solid ${record.tax_option === "Individual"
                            ? "rgba(16, 185, 129, 0.3)"
                            : "rgba(240, 147, 251, 0.3)"}`,
                          fontSize: "13px",
                          fontWeight: 600,
                        }}>
                          {record.tax_option}
                        </span>
                      </td>
                      <td>{record.num_people}</td>
                      <td style={{ fontWeight: 700, color: "#10b981" }}>
                        ${Math.floor(record.revenue).toLocaleString()}
                      </td>
                      <td style={{ color: "#ef4444" }}>
                        ${Math.floor(record.total_costs).toLocaleString()}
                      </td>
                      <td style={{ fontWeight: 700, color: "#667eea" }}>
                        ${Math.floor(record.net_income_group).toLocaleString()}
                      </td>
                      <td style={{ color: "#f59e0b" }}>
                        ${Math.floor(record.tax_amount * record.num_people).toLocaleString()}
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                          <button
                            onClick={() => window.open(`http://localhost:8000/api/export/record/${record.id}/pdf`, "_blank")}
                            className="btn-secondary"
                            style={{
                              padding: "6px 12px",
                              fontSize: "13px",
                              display: "flex",
                              alignItems: "center",
                              gap: "6px",
                            }}
                          >
                            📄 View
                          </button>
                          <button
                            onClick={() => handleEditClick(record, "revenue")}
                            className="btn-primary"
                            style={{ padding: "6px 12px", fontSize: "13px" }}
                          >
                            ✏️ Edit
                          </button>
                          {deleteConfirm === record.id ? (
                            <div style={{ display: "flex", gap: "4px" }}>
                              <button
                                onClick={() => handleDelete(record.id)}
                                className="btn-danger"
                                style={{ padding: "6px 12px", fontSize: "13px" }}
                              >
                                ✓ Confirm
                              </button>
                              <button
                                onClick={() => setDeleteConfirm(null)}
                                className="btn-secondary"
                                style={{ padding: "6px 12px", fontSize: "13px" }}
                              >
                                ✗ Cancel
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => setDeleteConfirm(record.id)}
                              className="btn-danger"
                              style={{ padding: "6px 12px", fontSize: "13px" }}
                            >
                              🗑️ Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginTop: "24px" }}>
        <div className="stat-card">
          <h4>Total Records</h4>
          <div className="stat-value">{filteredRecords.length}</div>
        </div>
        <div className="stat-card">
          <h4>Total Revenue</h4>
          <div className="stat-value">
            ${Math.floor(filteredRecords.reduce((sum, r) => sum + r.revenue, 0)).toLocaleString()}
          </div>
        </div>
        <div className="stat-card">
          <h4>Total Tax Paid</h4>
          <div className="stat-value">
            ${Math.floor(filteredRecords.reduce((sum, r) => sum + (r.tax_amount * r.num_people), 0)).toLocaleString()}
          </div>
        </div>
        <div className="stat-card">
          <h4>Total Net Income</h4>
          <div className="stat-value">
            ${Math.floor(filteredRecords.reduce((sum, r) => sum + r.net_income_group, 0)).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {editingRecord && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0, 0, 0, 0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }}>
          <div className="card" style={{
            maxWidth: "500px",
            width: "90%",
            padding: "32px",
          }}>
            <h3 style={{ marginBottom: "24px" }}>✏️ Edit Record #{editingRecord}</h3>

            <div className="form-group">
              <label>Field to Edit</label>
              <select
                value={editField}
                onChange={(e) => {
                  setEditField(e.target.value);
                  const record = records.find(r => r.id === editingRecord);
                  if (record) {
                    const value = (record as unknown as { [key: string]: unknown })[e.target.value];
                    setEditValue(String(value));
                  }
                }}
                className="form-control"
              >
                <option value="num_people">Number of People</option>
                <option value="revenue">Revenue</option>
                <option value="total_costs">Total Costs</option>
                <option value="tax_origin">Country</option>
                <option value="tax_option">Tax Type</option>
              </select>
            </div>

            <div className="form-group" style={{ marginTop: "16px" }}>
              <label>New Value</label>
              {editField === "tax_option" ? (
                <select
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="form-control"
                >
                  <option value="Individual">Individual</option>
                  <option value="Business">Business</option>
                </select>
              ) : editField === "tax_origin" ? (
                <select
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="form-control"
                >
                  <option value="US">US</option>
                  <option value="Spain">Spain</option>
                </select>
              ) : (
                <input
                  type={["num_people", "revenue", "total_costs"].includes(editField) ? "number" : "text"}
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="form-control"
                  step={editField === "num_people" ? "1" : "0.01"}
                />
              )}
            </div>

            <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
              <button
                onClick={handleEditSave}
                className="btn-primary"
                style={{ flex: 1 }}
              >
                💾 Save Changes
              </button>
              <button
                onClick={cancelEdit}
                className="btn-secondary"
                style={{ flex: 1 }}
              >
                ✗ Cancel
              </button>
            </div>

            <div style={{
              marginTop: "20px",
              padding: "12px",
              background: "rgba(251, 191, 36, 0.1)",
              border: "1px solid rgba(251, 191, 36, 0.3)",
              borderRadius: "8px",
              fontSize: "13px",
              color: "rgba(255, 255, 255, 0.8)",
            }}>
              ℹ️ Note: Updating revenue, costs, or people count will recalculate all derived fields (taxes, net income, etc.)
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordsManagement;
