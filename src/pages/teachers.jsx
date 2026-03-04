import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Teachers() {
  const [teachers, setTeachers] = useState([]);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Initial form state (subject_ids is an array to hold multiple selections)
  const initialFormState = { name: '', cnic: '', contact_number: '', subject_ids: [] };
  const [formData, setFormData] = useState(initialFormState);

  // Fetch BOTH teachers and subjects when the page loads
  const loadData = async () => {
    try {
      // Promise.all fetches both at the exact same time to make the page load faster
      const [teachersData, subjectsData] = await Promise.all([
        api.getTeachers(),
        api.getSubjects()
      ]);
      setTeachers(teachersData);
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

  // Handle standard text inputs
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle checking/unchecking subjects
  const handleSubjectToggle = (subjectId) => {
    setFormData((prev) => {
      const isSelected = prev.subject_ids.includes(subjectId);
      if (isSelected) {
        // Remove it if it was already checked
        return { ...prev, subject_ids: prev.subject_ids.filter(id => id !== subjectId) };
      } else {
        // Add it if it wasn't checked
        return { ...prev, subject_ids: [...prev.subject_ids, subjectId] };
      }
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ type: '', text: '' });

    if (!formData.name.trim()) {
      setMessage({ type: 'error', text: 'Instructor Name is required.' });
      setSubmitting(false);
      return;
    }
    if (formData.subject_ids.length === 0) {
      setMessage({ type: 'error', text: 'You must assign at least one subject to this instructor.' });
      setSubmitting(false);
      return;
    }

    try {
      await api.addTeacher(formData);
      setMessage({ type: 'success', text: 'Teacher profile created successfully!' });
      setFormData(initialFormState); // Clear the form
      
      // We only need to reload the teachers list, not the subjects
      const updatedTeachers = await api.getTeachers();
      setTeachers(updatedTeachers);
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to add teacher. CNIC might already exist.' });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle deletion
  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete ${name}'s profile?`)) return;
    try {
      await api.deleteTeacher(id);
      setTeachers(teachers.filter(teacher => teacher.id !== id));
      setMessage({ type: 'success', text: `${name} deleted successfully.` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Cannot delete teacher. They might be tied to an active schedule.' });
    }
  };

  // Inline styles
  const inputStyle = { width: '100%', padding: '10px', marginTop: '5px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #cbd5e1', boxSizing: 'border-box' };
  const labelStyle = { fontWeight: 'bold', color: '#475569', fontSize: '0.9rem' };
  const thStyle = { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e2e8f0', color: '#475569' };
  const tdStyle = { padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#1e293b' };

  if (loading) return <p>Loading faculty data...</p>;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>👨‍🏫 Manage Faculty</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Add instructors and select the specific curriculum subjects they are qualified to teach.</p>

      {message.text && (
        <div style={{ padding: '15px', marginBottom: '20px', borderRadius: '4px', backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b' }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
        
        {/* LEFT COLUMN: Add Form */}
        <div style={{ flex: '1 1 320px', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', alignSelf: 'flex-start' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>➕ Add Instructor</h2>
          
          {availableSubjects.length === 0 && (
            <div style={{ padding: '10px', backgroundColor: '#fef08a', color: '#854d0e', borderRadius: '4px', marginBottom: '15px', fontSize: '0.9rem' }}>
              ⚠️ Please add subjects in the 'Manage Subjects' page first.
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <label style={labelStyle}>Full Name</label>
            <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="e.g., Dr. Ali Raza" style={inputStyle} required />

            <label style={labelStyle}>CNIC (Optional)</label>
            <input type="text" name="cnic" value={formData.cnic} onChange={handleChange} placeholder="e.g., 31202-1234567-1" style={inputStyle} />

            <label style={labelStyle}>Contact Number (Optional)</label>
            <input type="text" name="contact_number" value={formData.contact_number} onChange={handleChange} placeholder="e.g., 0300-1234567" style={inputStyle} />

            {/* Scrollable Checkbox List for Subjects */}
            <label style={labelStyle}>Qualified to Teach:</label>
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
              {submitting ? 'Saving...' : 'Save Teacher Profile'}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Data Table */}
        <div style={{ flex: '2 1 500px' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>📋 Faculty Roster</h2>
          
          {teachers.length === 0 ? (
            <p style={{ color: '#64748b' }}>No faculty added yet.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Instructor Name</th>
                  <th style={thStyle}>Qualified Subjects</th>
                  <th style={thStyle}>Action</th>
                </tr>
              </thead>
              <tbody>
                {teachers.map((teacher) => (
                  <tr key={teacher.id} style={{ transition: 'background-color 0.2s' }}>
                    <td style={tdStyle}><strong>{teacher.name}</strong></td>
                    <td style={tdStyle}>
                      {/* Map through the nested subjects array returned from the backend */}
                      {teacher.subjects_can_teach && teacher.subjects_can_teach.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                          {teacher.subjects_can_teach.map(sub => (
                            <span key={sub.id} style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                              {sub.course_code}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No subjects assigned</span>
                      )}
                    </td>
                    <td style={tdStyle}>
                      <button onClick={() => handleDelete(teacher.id, teacher.name)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
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
