import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const register = (data) => api.post('/auth/register', data);
export const login = (data) => api.post('/auth/login', data);
export const getCurrentUser = () => api.get('/auth/me');

export const uploadReceipt = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/receipts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getReceipts = () => api.get('/receipts');
export const processReceipt = (id) => api.post(`/receipts/${id}/process`);
export const deleteReceipt = (id) => api.delete(`/receipts/${id}`);

export const getScore = () => api.get('/verification/score');
export const getScoreBreakdown = () => api.get('/verification/breakdown');
export const getDashboard = () => api.get('/users/dashboard');

export default api;
