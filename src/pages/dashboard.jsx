import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalRooms: 0,
    totalSubjects: 0,
    totalTeachers: 0,
    totalBatches: 0
  });
  const [loading, setLoading] = useState(true);

  // Fetch data when the component mounts
  useEffect(() => {
    async function loadStats() {
      try {
        // We will build this combined endpoint in the Python backend later
        const data = await api.getDashboardStats(); 
        setStats(data);
      } catch (error) {
        console.error("Failed to load dashboard stats", error);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  // Simple reusable card component for the metrics
  const MetricCard = ({ title, count, icon }) => (
    <div style={{ padding: '20px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', flex: 1, margin: '0 10px' }}>
      <div style={{ fontSize: '2rem', marginBottom: '10px' }}>{icon}</div>
      <h3 style={{ margin: '0 0 5px 0', color: '#64748b', fontSize: '0.9rem', textTransform: 'uppercase' }}>{title}</h3>
      <p style={{ margin: 0, fontSize: '1.8rem', fontWeight: 'bold', color: '#0f172a' }}>{count}</p>
    </div>
  );

  if (loading) return <p>Loading dashboard...</p>;

  // Check if all pillars are ready for the algorithm
  const isReady = stats.totalRooms > 0 && stats.totalSubjects > 0 && stats.totalTeachers > 0 && stats.totalBatches > 0;

  return (
    <div>
      <h1 style={{ color: '#1e293b', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>📊 System Overview</h1>
      <p style={{ color: '#64748b', marginBottom: '30px' }}>Welcome to the IUB AI Department Scheduling System.</p>

      {/* Metrics Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '0 -10px 40px -10px' }}>
        <MetricCard title="Total Rooms" count={stats.totalRooms} icon="🏫" />
        <MetricCard title="Curriculum Subjects" count={stats.totalSubjects} icon="📚" />
        <MetricCard title="Faculty Members" count={stats.totalTeachers} icon="👨‍🏫" />
        <MetricCard title="Active Sections" count={stats.totalBatches} icon="🎓" />
      </div>

      {/* Readiness Checklist */}
      <div style={{ backgroundColor: isReady ? '#ecfdf5' : '#fffbeb', padding: '20px', borderRadius: '8px', border: `1px solid ${isReady ? '#a7f3d0' : '#fde68a'}` }}>
        <h2 style={{ marginTop: 0, color: isReady ? '#065f46' : '#92400e', fontSize: '1.2rem' }}>
          {isReady ? '✅ System Ready for Generation' : '⚠️ Missing Data'}
        </h2>
        <p style={{ color: isReady ? '#047857' : '#b45309', marginBottom: '10px' }}>
          The optimization engine requires data in all four pillars before it can compute a clash-free schedule.
        </p>
        
        <ul style={{ listStyleType: 'none', padding: 0, color: '#334155' }}>
          <li>{stats.totalRooms > 0 ? '✅' : '❌'} Rooms & Labs Configured</li>
          <li>{stats.totalSubjects > 0 ? '✅' : '❌'} Curriculum Defined</li>
          <li>{stats.totalTeachers > 0 ? '✅' : '❌'} Faculty Added</li>
          <li>{stats.totalBatches > 0 ? '✅' : '❌'} Batches & Sections Created</li>
        </ul>
      </div>
    </div>
  );
}
