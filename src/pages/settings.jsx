import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Settings() {
  const [formData, setFormData] = useState({
    uni_open_time: '08:00',
    uni_close_time: '16:00',
    jumma_break_start: '13:00',
    jumma_break_end: '14:30',
    credit_hour_duration_mins: 60,
    sunday_off: true
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Load existing settings when the page loads
  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await api.getSettings();
        if (data) {
          // Format time strings to 'HH:MM' for the HTML time input
          setFormData({
            ...data,
            uni_open_time: data.uni_open_time.substring(0, 5),
            uni_close_time: data.uni_close_time.substring(0, 5),
            jumma_break_start: data.jumma_break_start.substring(0, 5),
            jumma_break_end: data.jumma_break_end.substring(0, 5),
          });
        }
      } catch (error) {
        setMessage({ type: 'error', text: 'Failed to load settings from server.' });
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  // Handle generic input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Submit the updated settings to the API
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    // Basic Validation
    if (formData.uni_open_time >= formData.uni_close_time) {
      setMessage({ type: 'error', text: 'Open Time must be earlier than Close Time.' });
      setSaving(false);
      return;
    }
    if (formData.jumma_break_start >= formData.jumma_break_end) {
      setMessage({ type: 'error', text: 'Jumma Break Start must be earlier than End time.' });
      setSaving(false);
      return;
    }

    try {
      await api.updateSettings(formData);
      setMessage({ type: 'success', text: 'Global settings updated successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings.' });
    } finally {
      setSaving(false);
    }
  };

  // Shared inline styles for form inputs
  const inputStyle = {
    width: '100%', padding: '10px', marginTop: '5px', marginBottom: '20px',
    borderRadius: '4px', border: '1px solid #cbd5e1', boxSizing: 'border-box'
  };

  const labelStyle = { fontWeight: 'bold', color: '#475569', fontSize: '0.9rem' };

  if (loading) return <p>Loading settings...</p>;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>⚙️ Global Settings</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Configure the master rules for the optimization algorithm.</p>

      {/* Alert Message Box */}
      {message.text && (
        <div style={{
          padding: '15px', marginBottom: '20px', borderRadius: '4px',
          backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2',
          color: message.type === 'success' ? '#166534' : '#991b1b',
          border: `1px solid ${message.type === 'success' ? '#bbf7d0' : '#fecaca'}`
        }}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ maxWidth: '600px' }}>
        
        {/* Operating Hours Block */}
        <div style={{ display: 'flex', gap: '20px' }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>University Open Time</label>
            <input type="time" name="uni_open_time" value={formData.uni_open_time} onChange={handleChange} style={inputStyle} required />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>University Close Time</label>
            <input type="time" name="uni_close_time" value={formData.uni_close_time} onChange={handleChange} style={inputStyle} required />
          </div>
        </div>

        {/* Jumma Break Block */}
        <div style={{ display: 'flex', gap: '20px' }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Jumma Break Start</label>
            <input type="time" name="jumma_break_start" value={formData.jumma_break_start} onChange={handleChange} style={inputStyle} required />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Jumma Break End</label>
            <input type="time" name="jumma_break_end" value={formData.jumma_break_end} onChange={handleChange} style={inputStyle} required />
          </div>
        </div>

        {/* Academic Rules Block */}
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Duration of 1 Credit Hour (Minutes)</label>
            <input type="number" name="credit_hour_duration_mins" value={formData.credit_hour_duration_mins} onChange={handleChange} min="30" max="120" step="5" style={inputStyle} required />
          </div>
          <div style={{ flex: 1, marginTop: '-15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', ...labelStyle }}>
              <input type="checkbox" name="sunday_off" checked={formData.sunday_off} onChange={handleChange} style={{ marginRight: '10px', width: '18px', height: '18px' }} />
              Keep Sunday Completely Off
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={saving} style={{
          backgroundColor: saving ? '#94a3b8' : '#2563eb', color: 'white', border: 'none',
          padding: '12px 20px', borderRadius: '4px', cursor: saving ? 'not-allowed' : 'pointer',
          fontWeight: 'bold', width: '100%', marginTop: '10px', transition: 'background-color 0.2s'
        }}>
          {saving ? 'Saving...' : '💾 Save Global Settings'}
        </button>

      </form>
    </div>
  );
}
