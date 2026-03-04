// Base URL for your Python FastAPI backend
const API_BASE_URL = 'http://localhost:8000/api';

// Helper function to handle API responses cleanly
async function fetchFromAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'API request failed');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
}

// ==========================================
// ENDPOINT FUNCTIONS
// ==========================================

export const api = {
  // Dashboard & Settings
  getDashboardStats: () => fetchFromAPI('/stats'),
  getSettings: () => fetchFromAPI('/settings'),
  updateSettings: (data) => fetchFromAPI('/settings', { method: 'PUT', body: JSON.stringify(data) }),

  // Rooms
  getRooms: () => fetchFromAPI('/rooms'),
  addRoom: (data) => fetchFromAPI('/rooms', { method: 'POST', body: JSON.stringify(data) }),
  deleteRoom: (id) => fetchFromAPI(`/rooms/${id}`, { method: 'DELETE' }),

  // Subjects
  getSubjects: () => fetchFromAPI('/subjects'),
  addSubject: (data) => fetchFromAPI('/subjects', { method: 'POST', body: JSON.stringify(data) }),
  deleteSubject: (id) => fetchFromAPI(`/subjects/${id}`, { method: 'DELETE' }),

  // Teachers
  getTeachers: () => fetchFromAPI('/teachers'),
  addTeacher: (data) => fetchFromAPI('/teachers', { method: 'POST', body: JSON.stringify(data) }),
  deleteTeacher: (id) => fetchFromAPI(`/teachers/${id}`, { method: 'DELETE' }),

  // Batches
  getBatches: () => fetchFromAPI('/batches'),
  addBatch: (data) => fetchFromAPI('/batches', { method: 'POST', body: JSON.stringify(data) }),
  deleteBatch: (id) => fetchFromAPI(`/batches/${id}`, { method: 'DELETE' }),

  // Algorithm Engine
  generateTimetable: () => fetchFromAPI('/generate', { method: 'POST' })
};
