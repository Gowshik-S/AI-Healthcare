/**
 * Healthcare Triage - API Client
 * Fetch wrapper for all backend API calls
 */

const API_BASE_URL = 'http://localhost:8001';

/**
 * Generic fetch wrapper with auth headers and error handling
 */
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'API request failed');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Auth endpoints
const authAPI = {
  login: (email, password) => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),
  
  register: (userData) => apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),
  
  getCurrentUser: () => apiRequest('/auth/me'),
};

// Patient endpoints
const patientAPI = {
  getProfile: () => apiRequest('/patients/profile'),
  
  updateProfile: (data) => apiRequest('/patients/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  getHistory: () => apiRequest('/patients/history'),
};

// Triage endpoints
const triageAPI = {
  startSession: () => apiRequest('/triage/start', { method: 'POST' }),
  
  addSymptom: (sessionId, symptomId) => apiRequest('/triage/add-symptom', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, symptom_id: symptomId }),
  }),
  
  getResult: (sessionId) => apiRequest(`/triage/result/${sessionId}`),
  
  getSymptoms: () => apiRequest('/triage/symptoms'),
};

// Consultation endpoints
const consultationAPI = {
  getAll: () => apiRequest('/consultations/all'),
  
  getDetails: (id) => apiRequest(`/consultations/${id}`),
  
  create: (data) => apiRequest('/consultations/create', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

// Prescription endpoints
const prescriptionAPI = {
  getByConsultation: (consultationId) => apiRequest(`/prescriptions/${consultationId}`),
  
  add: (data) => apiRequest('/prescriptions/add', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

// Doctor endpoints
const doctorAPI = {
  getProfile: () => apiRequest('/doctors/profile'),
  
  createProfile: (data) => apiRequest('/doctors/profile', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  getPatients: () => apiRequest('/doctors/patients'),
  
  getPatientDetails: (patientId) => apiRequest(`/doctors/patients/${patientId}`),
};

// Export for use in other modules
window.API = {
  auth: authAPI,
  patient: patientAPI,
  triage: triageAPI,
  consultation: consultationAPI,
  prescription: prescriptionAPI,
  doctor: doctorAPI,
};
