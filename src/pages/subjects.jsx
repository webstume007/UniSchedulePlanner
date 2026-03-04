import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Initial form state
  const initialFormState = { course_code: '', subject_name: '', total_credit_hours: 3, requires_lab: false };
  const [formData, setFormData] = useState(initialFormState);

  // Fetch subjects from the database
  const loadSubjects = async () => {
    try {
      const data = await api.getSubjects();
      setSubjects(data);
    } catch (error) {
      console.error("Failed to load subjects", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubjects();
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ type: '', text: '' });

    if (!formData.course_code.trim() || !formData.subject_name.trim()) {
      setMessage({ type: 'error', text: 'Course Code and Subject Name are required.' });
      setSubmitting(false);
      return;
    }

    // Auto-uppercase the course code (e.g., aif-301 -> AIF-301)
    const payload = {
      ...formData,
      course_code: formData.course_code.trim().toUpperCase()
    };

    try {
      await api.addSubject(payload);
      setMessage({ type: 'success', text: 'Subject added successfully!' });
      setFormData(initialFormState); // Clear the form
      loadSubjects(); // Refresh the table
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to add subject (Code might already exist).' });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle deletion
  const handleDelete = async (id, code) => {
    if (!window.confirm(`Are you sure you want to delete ${code}?`)) return;
    
    try {
      await api.deleteSubject(id);
      setSubjects(subjects.filter(sub => sub.id !== id));
      setMessage({ type: 'success', text: `${code} deleted successfully.` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Cannot delete subject. It might already be assigned to a teacher or batch.' });
    }
  };

  // Inline styles (reused for consistency)
  const inputStyle = { width: '100%', padding: '10px', marginTop: '5px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #cbd5e1', boxSizing: 'border-box' };
  const labelStyle = { fontWeight: 'bold', color: '#475569', fontSize: '0.9rem' };
  const thStyle = { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e2e8f0', color: '#475569' };
  const tdStyle = { padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#1e293b' };

  if (loading) return <p>Loading curriculum...</p>;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>📚 Manage Subjects</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Define the courses taught in the AI department. You must add subjects here before assigning them to Teachers or Batches.</p>

      {message.text && (
        <div style={{ padding: '15px', marginBottom: '20px', borderRadius: '4px', backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b' }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
        
        {/* LEFT COLUMN: Add Form */}
        <div style={{ flex: '1 1 300px', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', alignSelf: 'flex-start' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>➕ Add New Subject</h2>
          <form onSubmit={handleSubmit}>
            <label style={labelStyle}>Course Code</label>
            <input type="text" name="course_code" value={formData.course_code} onChange={handleChange} placeholder="e.g., AIF-301" style={inputStyle} required />

            <label style={labelStyle}>Subject Name</label>
            <input type="text" name="subject_name" value={formData.subject_name} onChange={handleChange} placeholder="e.g., Artificial Intelligence" style={inputStyle} required />

            <label style={labelStyle}>Total Credit Hours</label>
            <input type="number" name="total_credit_hours" value={formData.total_credit_hours} onChange={handleChange} min="1" max="6" step="1" style={inputStyle} required />

            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', ...labelStyle, marginBottom: '20px' }}>
              <input type="checkbox" name="requires_lab" checked={formData.requires_lab} onChange={handleChange} style={{ marginRight: '10px', width: '18px', height: '18px' }} />
              🧪 Requires Computer Lab
            </label>

            <button type="submit" disabled={submitting} style={{ backgroundColor: submitting ? '#94a3b8' : '#3b82f6', color: 'white', border: 'none', padding: '10px 15px', borderRadius: '4px', cursor: submitting ? 'not-allowed' : 'pointer', fontWeight: 'bold', width: '100%' }}>
              {submitting ? 'Saving...' : 'Save Subject'}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Data Table */}
        <div style={{ flex: '2 1 500px' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>📋 Existing Curriculum</h2>
          
          {subjects.length === 0 ? (
            <p style={{ color: '#64748b' }}>No subjects added yet. Use the form on the left to build the curriculum.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Code</th>
                  <th style={thStyle}>Subject Name</th>
                  <th style={thStyle}>Cr. Hrs</th>
                  <th style={thStyle}>Type</th>
                  <th style={thStyle}>Action</th>
                </tr>
              </thead>
              <tbody>
                {subjects.map((subject) => (
                  <tr key={subject.id} style={{ transition: 'background-color 0.2s' }}>
                    <td style={tdStyle}><span style={{ backgroundColor: '#e2e8f0', padding: '2px 6px', borderRadius: '4px', fontFamily: 'monospace' }}>{subject.course_code}</span></td>
                    <td style={tdStyle}><strong>{subject.subject_name}</strong></td>
                    <td style={tdStyle}>{subject.total_credit_hours}</td>
                    <td style={tdStyle}>{subject.requires_lab ? '🧪 Lab' : '📚 Theory'}</td>
                    <td style={tdStyle}>
                      <button onClick={() => handleDelete(subject.id, subject.course_code)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
                        🗑️ Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  );
}
