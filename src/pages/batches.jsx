import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Batches() {
  const [batches, setBatches] = useState([]);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Initial form state
  const initialFormState = { semester_level: 3, section_name: '', student_strength: 50, subject_ids: [] };
  const [formData, setFormData] = useState(initialFormState);

  // Fetch BOTH batches and subjects
  const loadData = async () => {
    try {
      const [batchesData, subjectsData] = await Promise.all([
        api.getBatches(),
        api.getSubjects()
      ]);
      setBatches(batchesData);
      setAvailableSubjects(subjectsData);
    } catch (error) {
      console.error("Failed to load data", error);
      setMessage({ type: 'error', text: 'Failed to connect to the database.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Handle standard inputs
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseInt(value) : value
    });
  };

  // Handle checking/unchecking subjects
  const handleSubjectToggle = (subjectId) => {
    setFormData((prev) => {
      const isSelected = prev.subject_ids.includes(subjectId);
      if (isSelected) {
        return { ...prev, subject_ids: prev.subject_ids.filter(id => id !== subjectId) };
      } else {
        return { ...prev, subject_ids: [...prev.subject_ids, subjectId] };
      }
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ type: '', text: '' });

    if (!formData.section_name.trim()) {
      setMessage({ type: 'error', text: 'Section Name is required.' });
      setSubmitting(false);
      return;
    }
    if (formData.subject_ids.length === 0) {
      setMessage({ type: 'error', text: 'You must assign at least one subject to this batch.' });
      setSubmitting(false);
      return;
    }

    // Auto-uppercase section (e.g., 'a' -> 'A')
    const payload = {
      ...formData,
      section_name: formData.section_name.trim().toUpperCase()
    };

    try {
      await api.addBatch(payload);
      setMessage({ type: 'success', text: 'Batch & curriculum assigned successfully!' });
      setFormData(initialFormState);
      
      const updatedBatches = await api.getBatches();
      setBatches(updatedBatches);
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to add batch.' });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle deletion
  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete ${title}?`)) return;
    try {
      await api.deleteBatch(id);
      setBatches(batches.filter(batch => batch.id !== id));
      setMessage({ type: 'success', text: `${title} deleted successfully.` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Cannot delete batch. It might be tied to an active schedule.' });
    }
  };

  // Sorting batches by semester level so the table looks organized
  const sortedBatches = [...batches].sort((a, b) => {
    if (a.semester_level !== b.semester_level) return a.semester_level - b.semester_level;
    return a.section_name.localeCompare(b.section_name);
  });

  // Inline styles
  const inputStyle = { width: '100%', padding: '10px', marginTop: '5px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #cbd5e1', boxSizing: 'border-box' };
  const labelStyle = { fontWeight: 'bold', color: '#475569', fontSize: '0.9rem' };
  const thStyle = { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e2e8f0', color: '#475569' };
  const tdStyle = { padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#1e293b' };

  if (loading) return <p>Loading batch data...</p>;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>🎓 Manage Batches & Sections</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Define semesters, sections, student counts, and assign the curriculum for each batch.</p>

      {message.text && (
        <div style={{ padding: '15px', marginBottom: '20px', borderRadius: '4px', backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b' }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
        
        {/* LEFT COLUMN: Add Form */}
        <div style={{ flex: '1 1 320px', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', alignSelf: 'flex-start' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>➕ Add New Section</h2>
          
          {availableSubjects.length === 0 && (
            <div style={{ padding: '10px', backgroundColor: '#fef08a', color: '#854d0e', borderRadius: '4px', marginBottom: '15px', fontSize: '0.9rem' }}>
              ⚠️ Please add subjects to the curriculum first.
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <label style={labelStyle}>Semester Level</label>
            <input type="number" name="semester_level" value={formData.semester_level} onChange={handleChange} min="1" max="8" style={inputStyle} required title="e.g., 3 for 3rd Semester" />

            <label style={labelStyle}>Section Name</label>
            <input type="text" name="section_name" value={formData.section_name} onChange={handleChange} placeholder="e.g., A, B, or Morning" style={inputStyle} required />

            <label style={labelStyle}>Student Strength</label>
            <input type="number" name="student_strength" value={formData.student_strength} onChange={handleChange} min="5" max="300" step="5" style={inputStyle} required title="Total students in this specific section." />

            {/* Scrollable Checkbox List for Subjects */}
            <label style={labelStyle}>Assign Curriculum (Subjects):</label>
            <div style={{ border: '1px solid #cbd5e1', borderRadius: '4px', padding: '10px', maxHeight: '150px', overflowY: 'auto', backgroundColor: 'white', marginBottom: '20px', marginTop: '5px' }}>
              {availableSubjects.map(subject => (
                <label key={subject.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', cursor: 'pointer', fontSize: '0.9rem', color: '#334155' }}>
                  <input 
                    type="checkbox" 
                    checked={formData.subject_ids.includes(subject.id)}
                    onChange={() => handleSubjectToggle(subject.id)}
                    style={{ marginRight: '10px' }}
                  />
                  <span style={{ fontWeight: 'bold', marginRight: '5px' }}>{subject.course_code}</span> - {subject.subject_name}
                </label>
              ))}
            </div>

            <button type="submit" disabled={submitting || availableSubjects.length === 0} style={{ backgroundColor: submitting || availableSubjects.length === 0 ? '#94a3b8' : '#3b82f6', color: 'white', border: 'none', padding: '10px 15px', borderRadius: '4px', cursor: submitting || availableSubjects.length === 0 ? 'not-allowed' : 'pointer', fontWeight: 'bold', width: '100%' }}>
              {submitting ? 'Saving...' : 'Save Batch Profile'}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Data Table */}
        <div style={{ flex: '2 1 500px' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>📋 Active Batches</h2>
          
          {sortedBatches.length === 0 ? (
            <p style={{ color: '#64748b' }}>No batches added yet.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Semester & Section</th>
                  <th style={thStyle}>Strength</th>
                  <th style={thStyle}>Curriculum</th>
                  <th style={thStyle}>Action</th>
                </tr>
              </thead>
              <tbody>
                {sortedBatches.map((batch) => {
                  const title = `Semester ${batch.semester_level} - ${batch.section_name}`;
                  return (
                    <tr key={batch.id} style={{ transition: 'background-color 0.2s' }}>
                      <td style={tdStyle}><strong>{title}</strong></td>
                      <td style={tdStyle}>👥 {batch.student_strength}</td>
                      <td style={tdStyle}>
                        {batch.curriculum_subjects && batch.curriculum_subjects.length > 0 ? (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                            {batch.curriculum_subjects.map(sub => (
                              <span key={sub.id} style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                                {sub.course_code}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No subjects</span>
                        )}
                      </td>
                      <td style={tdStyle}>
                        <button onClick={() => handleDelete(batch.id, title)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  );
}
