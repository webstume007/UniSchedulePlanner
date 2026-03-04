import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  // Styles for our navigation links to show which one is currently active
  const navLinkStyle = ({ isActive }) => ({
    display: 'block',
    padding: '10px 15px',
    margin: '5px 0',
    color: isActive ? '#ffffff' : '#cbd5e1',
    backgroundColor: isActive ? '#3b82f6' : 'transparent',
    textDecoration: 'none',
    borderRadius: '6px',
    fontWeight: isActive ? 'bold' : 'normal',
    transition: 'background-color 0.2s'
  });

  return (
    <div style={{ width: '260px', backgroundColor: '#1e293b', color: '#ffffff', padding: '20px', display: 'flex', flexDirection: 'column' }}>
      
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem', color: '#60a5fa' }}>📅 AI Dept Timetable</h2>
        <p style={{ margin: '5px 0 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>IUB Management System</p>
      </div>

      <nav style={{ flex: 1 }}>
        <NavLink to="/" style={navLinkStyle}>📊 Dashboard</NavLink>
        <NavLink to="/settings" style={navLinkStyle}>⚙️ Global Settings</NavLink>
        <NavLink to="/rooms" style={navLinkStyle}>🏫 Manage Rooms</NavLink>
        <NavLink to="/subjects" style={navLinkStyle}>📚 Manage Subjects</NavLink>
        <NavLink to="/teachers" style={navLinkStyle}>👨‍🏫 Manage Faculty</NavLink>
        <NavLink to="/batches" style={navLinkStyle}>🎓 Manage Batches</NavLink>
        <NavLink to="/generate" style={navLinkStyle}>🚀 Generate Timetable</NavLink>
      </nav>

      <div style={{ borderTop: '1px solid #334155', paddingTop: '15px', fontSize: '0.75rem', color: '#64748b' }}>
        <p>System Status: Ready</p>
      </div>
      
    </div>
  );
}
