/**
 * API Service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';

// Use relative URL in production/Docker, absolute in development
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000/api');

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  // Don't set default Content-Type - let axios set it automatically based on data type
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Don't override Content-Type for FormData - let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    
    // Handle blob error responses
    if (error.response?.data instanceof Blob && error.config?.responseType === 'blob') {
      try {
        const text = await error.response.data.text();
        const errorData = JSON.parse(text);
        error.response.data = errorData;
      } catch {
        // If not JSON, keep as blob
      }
    }
    
    if (error.response?.status === 401 || error.response?.status === 422) {
      console.error('Auth error - clearing token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (error.response?.status === 422) {
        // 422 means invalid token - redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: (username, email, password) =>
    api.post('/register', { username, email, password }),
  
  login: (username, password) =>
    api.post('/login', { username, password }),
  
  getCurrentUser: () =>
    api.get('/me'),
};

// File API
export const fileAPI = {
  upload: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    // Don't set Content-Type - let axios set it automatically with boundary
    // The Authorization header will be added by the interceptor
    return api.post('/upload', formData, {
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onUploadProgress(percentCompleted);
        }
      },
    });
  },
  
  list: () =>
    api.get('/files'),
  
  download: (fileId) =>
    api.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    }),
  
  delete: (fileId) =>
    api.delete(`/files/${fileId}`),
  
  encryptFile: (formData) =>
    api.post('/encrypt', formData, {
      responseType: 'blob',
    }),
  
  decryptFile: (formData) =>
    api.post('/decrypt', formData, {
      responseType: 'blob',
    }),
  
  sftpUpload: (formData) =>
    api.post('/sftp/upload', formData),
  
  sftpDownload: (data) =>
    api.post('/sftp/download', data, {
      responseType: 'blob',
    }),
};

// Admin API
export const adminAPI = {
  getLogs: (limit = 100) =>
    api.get('/admin/logs', { params: { limit } }),
  
  getTransfers: () =>
    api.get('/admin/transfers'),
  
  getUsers: () =>
    api.get('/admin/users'),
};

export default api;

