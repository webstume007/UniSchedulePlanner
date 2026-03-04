import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// We will create these page components one by one next
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Rooms from './pages/Rooms';
import Subjects from './pages/Subjects';
import Teachers from './pages/Teachers';
import Batches from './pages/Batches';
import Timetable from './pages/Timetable';

export default function App() {
  return (
    <Router>
      {/* Main Layout Wrapper */}
      <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f3f4f6', fontFamily: 'sans-serif' }}>
        
        {/* Left Sidebar Navigation */}
        <Sidebar />

        {/* Right Content Area */}
        <div style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', backgroundColor: '#ffffff', padding: '2rem', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            
            {/* The Routes determine which page loads based on the URL */}
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/rooms" element={<Rooms />} />
              <Route path="/subjects" element={<Subjects />} />
              <Route path="/teachers" element={<Teachers />} />
              <Route path="/batches" element={<Batches />} />
              <Route path="/generate" element={<Timetable />} />
            </Routes>

          </div>
        </div>

      </div>
    </Router>
  );
}
