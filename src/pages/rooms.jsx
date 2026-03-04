import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Rooms() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Initial form state
  const initialFormState = { room_name: '', capacity: 50, is_lab: false };
  const [formData, setFormData] = useState(initialFormState);

  // Fetch rooms from the database
  const loadRooms = async () => {
    try {
      const data = await api.getRooms();
      setRooms(data);
    } catch (error) {
      console.error("Failed to load rooms", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRooms();
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

    if (!formData.room_name.trim()) {
      setMessage({ type: 'error', text: 'Room Name cannot be empty.' });
      setSubmitting(false);
      return;
    }

    try {
      await api.addRoom(formData);
      setMessage({ type: 'success', text: 'Room added successfully!' });
      setFormData(initialFormState); // Clear the form
      loadRooms(); // Refresh the table
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to add room.' });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle deletion
  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete ${name}?`)) return;
    
    try {
      await api.deleteRoom(id);
      // Instantly remove the room from the UI state without needing another API call
      setRooms(rooms.filter(room => room.id !== id));
      setMessage({ type: 'success', text: `${name} deleted successfully.` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete room.' });
    }
  };

  // Inline styles
  const inputStyle = { width: '100%', padding: '10px', marginTop: '5px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #cbd5e1', boxSizing: 'border-box' };
  const labelStyle = { fontWeight: 'bold', color: '#475569', fontSize: '0.9rem' };
  const thStyle = { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e2e8f0', color: '#475569' };
  const tdStyle = { padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#1e293b' };

  if (loading) return <p>Loading rooms...</p>;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>🏫 Manage Rooms & Labs</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Add classrooms and computer labs, define their capacities, and manage existing spaces.</p>

      {message.text && (
        <div style={{ padding: '15px', marginBottom: '20px', borderRadius: '4px', backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b' }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
        
        {/* LEFT COLUMN: Add Form */}
        <div style={{ flex: '1 1 300px', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', alignSelf: 'flex-start' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>➕ Add New Space</h2>
          <form onSubmit={handleSubmit}>
            <label style={labelStyle}>Room Name / Number</label>
            <input type="text" name="room_name" value={formData.room_name} onChange={handleChange} placeholder="e.g., Room 304, AI Lab 1" style={inputStyle} required />

            <label style={labelStyle}>Maximum Student Capacity</label>
            <input type="number" name="capacity" value={formData.capacity} onChange={handleChange} min="10" max="300" step="5" style={inputStyle} required />

            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', ...labelStyle, marginBottom: '20px' }}>
              <input type="checkbox" name="is_lab" checked={formData.is_lab} onChange={handleChange} style={{ marginRight: '10px', width: '18px', height: '18px' }} />
              🧪 This is a Computer/Hardware Lab
            </label>

            <button type="submit" disabled={submitting} style={{ backgroundColor: submitting ? '#94a3b8' : '#3b82f6', color: 'white', border: 'none', padding: '10px 15px', borderRadius: '4px', cursor: submitting ? 'not-allowed' : 'pointer', fontWeight: 'bold', width: '100%' }}>
              {submitting ? 'Saving...' : 'Save Room'}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Data Table */}
        <div style={{ flex: '2 1 500px' }}>
          <h2 style={{ fontSize: '1.2rem', marginTop: 0, color: '#0f172a' }}>📋 Existing Rooms</h2>
          
          {rooms.length === 0 ? (
            <p style={{ color: '#64748b' }}>No rooms added yet. Use the form on the left to add your first room.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Room Name</th>
                  <th style={thStyle}>Capacity</th>
                  <th style={thStyle}>Type</th>
                  <th style={thStyle}>Action</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((room) => (
                  <tr key={room.id} style={{ transition: 'background-color 0.2s' }}>
                    <td style={tdStyle}><strong>{room.room_name}</strong></td>
                    <td style={tdStyle}>👥 {room.capacity}</td>
                    <td style={tdStyle}>{room.is_lab ? '🧪 Lab' : '🏫 Class'}</td>
                    <td style={tdStyle}>
                      <button onClick={() => handleDelete(room.id, room.room_name)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
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
