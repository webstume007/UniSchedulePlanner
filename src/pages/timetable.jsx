import React, { useState, useMemo } from 'react';
import { api } from '../services/api';

export default function Timetable() {
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Tab management
  const [activeTab, setActiveTab] = useState('master'); // 'master', 'batch', 'teacher', 'room'
  const [filterValue, setFilterValue] = useState(''); // Stores the selected dropdown value

  const handleGenerate = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    setSchedule(null);

    try {
      // Calls the Python OR-Tools Engine
      const result = await api.generateTimetable();
      setSchedule(result);
      setMessage({ type: 'success', text: '✅ Timetable generated successfully! Zero clashes detected.' });
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Algorithm could not find a clash-free combination. Try adding more rooms or teachers.' });
    } finally {
      setLoading(false);
    }
  };

  // Helper to get unique values for the dropdown filters
  const getUniqueValues = (key) => {
    if (!schedule) return [];
    return [...new Set(schedule.map(item => item[key]))].sort();
  };

  // Derived data for dropdowns
  const batches = useMemo(() => getUniqueValues('batch'), [schedule]);
  const teachers = useMemo(() => getUniqueValues('teacher'), [schedule]);
  const rooms = useMemo(() => getUniqueValues('room'), [schedule]);

  // Filter the schedule based on the active tab and selected dropdown value
  const filteredSchedule = useMemo(() => {
    if (!schedule) return [];
    if (activeTab === 'master') return schedule;
    if (!filterValue) return [];
    
    return schedule.filter(item => item[activeTab] === filterValue);
  }, [schedule, activeTab, filterValue]);

  // Handle Tab Switching
  const switchTab = (tab) => {
    setActiveTab(tab);
    setFilterValue(''); // Reset dropdown when changing tabs
  };

  // Inline styles
  const btnStyle = { padding: '12px 24px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', fontSize: '1rem', fontWeight: 'bold', cursor: 'pointer', transition: 'background-color 0.2s' };
  const tabStyle = (isActive) => ({ padding: '10px 20px', cursor: 'pointer', borderBottom: isActive ? '3px solid #3b82f6' : '3px solid transparent', color: isActive ? '#3b82f6' : '#64748b', fontWeight: isActive ? 'bold' : 'normal', backgroundColor: 'transparent', borderTop: 'none', borderLeft: 'none', borderRight: 'none', fontSize: '1rem' });
  const thStyle = { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e2e8f0', color: '#475569', backgroundColor: '#f8fafc' };
  const tdStyle = { padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#1e293b' };

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>🚀 Generate & View Timetable</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Run the optimization algorithm to create a clash-free schedule based on your constraints.</p>

      {/* Generator Control Panel */}
      <div style={{ padding: '20px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '30px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#0f172a' }}>Control Panel</h2>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem' }}>This may take a few seconds depending on the complexity of your data.</p>
        </div>
        <button onClick={handleGenerate} disabled={loading} style={{ ...btnStyle, backgroundColor: loading ? '#94a3b8' : '#10b981', cursor: loading ? 'wait' : 'pointer' }}>
          {loading ? '⏳ Crunching combinations...' : '⚡ Run Algorithm'}
        </button>
      </div>

      {message.text && (
        <div style={{ padding: '15px', marginBottom: '30px', borderRadius: '4px', backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b', border: `1px solid ${message.type === 'success' ? '#bbf7d0' : '#fecaca'}` }}>
          {message.text}
        </div>
      )}

      {/* Results View */}
      {schedule && (
        <div style={{ animation: 'fadeIn 0.5s' }}>
          
          {/* Custom Tab Navigation */}
          <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0', marginBottom: '20px' }}>
            <button onClick={() => switchTab('master')} style={tabStyle(activeTab === 'master')}>🗄️ Master Table</button>
            <button onClick={() => switchTab('batch')} style={tabStyle(activeTab === 'batch')}>🎓 View by Batch</button>
            <button onClick={() => switchTab('teacher')} style={tabStyle(activeTab === 'teacher')}>👨‍🏫 View by Teacher</button>
            <button onClick={() => switchTab('room')} style={tabStyle(activeTab === 'room')}>🏫 View by Room</button>
          </div>

          {/* Dynamic Dropdown Filters for specific tabs */}
          {activeTab !== 'master' && (
            <div style={{ marginBottom: '20px' }}>
              <select 
                value={filterValue} 
                onChange={(e) => setFilterValue(e.target.value)}
                style={{ padding: '10px', borderRadius: '4px', border: '1px solid #cbd5e1', minWidth: '300px', fontSize: '1rem' }}
              >
                <option value="" disabled>Select a {activeTab} to view...</option>
                {activeTab === 'batch' && batches.map(b => <option key={b} value={b}>{b}</option>)}
                {activeTab === 'teacher' && teachers.map(t => <option key={t} value={t}>{t}</option>)}
                {activeTab === 'room' && rooms.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          )}

          {/* Data Table */}
          {activeTab !== 'master' && !filterValue ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', border: '1px dashed #cbd5e1', borderRadius: '8px' }}>
              Please select an option from the dropdown above to view the schedule.
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white' }}>
                <thead>
                  <tr>
                    <th style={thStyle}>Day</th>
                    <th style={thStyle}>Time</th>
                    {activeTab !== 'batch' && <th style={thStyle}>Batch / Class</th>}
                    <th style={thStyle}>Subject</th>
                    {activeTab !== 'teacher' && <th style={thStyle}>Teacher</th>}
                    {activeTab !== 'room' && <th style={thStyle}>Room</th>}
                  </tr>
                </thead>
                <tbody>
                  {filteredSchedule.map((row, index) => (
                    <tr key={index} style={{ transition: 'background-color 0.2s', backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8fafc' }}>
                      <td style={tdStyle}><strong>{row.day}</strong></td>
                      <td style={tdStyle}>{row.time}</td>
                      {activeTab !== 'batch' && <td style={tdStyle}>{row.batch}</td>}
                      <td style={tdStyle}><span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 6px', borderRadius: '4px', fontFamily: 'monospace' }}>{row.subject}</span></td>
                      {activeTab !== 'teacher' && <td style={tdStyle}>{row.teacher}</td>}
                      {activeTab !== 'room' && <td style={tdStyle}>{row.room}</td>}
                    </tr>
                  ))}
                  {filteredSchedule.length === 0 && (
                    <tr>
                      <td colSpan="6" style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>No classes scheduled for this selection.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
