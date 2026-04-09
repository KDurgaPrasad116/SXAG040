import axios from 'axios';

// Base instance pointed at the FastAPI server root
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Convenience wrappers that prefix /api for feature routes
export const apiGet = (path, config) => api.get(`/api${path}`, config);
export const apiPost = (path, data, config) => api.post('/api${path}', data, config);

export default api;

