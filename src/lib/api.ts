/**
 * API Configuration and Helper
 * Centralized API endpoint management
 */

// Get API URL from environment or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export { API_URL };

/**
 * Fetch wrapper with error handling
 */
export async function apiCall(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<any> {
  const url = `${API_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Call Failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Prediction API
 */
export const predictAPI = {
  predict: (data: any, token?: string) =>
    apiCall('/api/predict', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token),
  
  batchPredict: (data: any, token?: string) =>
    apiCall('/api/batch-predict', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token),
  
  history: (token?: string) =>
    apiCall('/api/predictions-history', { method: 'GET' }, token),
};

/**
 * Auth API
 */
export const authAPI = {
  sendOTP: (email: string) =>
    apiCall('/api/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),
  
  verifyOTP: (email: string, otp: string) =>
    apiCall('/api/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ email, otp }),
    }),
  
  me: (token?: string) =>
    apiCall('/api/auth/me', { method: 'GET' }, token),
  
  logout: (token?: string) =>
    apiCall('/api/auth/logout', { method: 'POST' }, token),
};

/**
 * Student API
 */
export const studentAPI = {
  getProfile: (token?: string) =>
    apiCall('/api/student/profile', { method: 'GET' }, token),
  
  updateProfile: (data: any, token?: string) =>
    apiCall('/api/student/profile', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token),
};

/**
 * Admin API
 */
export const adminAPI = {
  getStudents: (token?: string) =>
    apiCall('/api/admin/students', { method: 'GET' }, token),
  
  getAnalytics: (token?: string) =>
    apiCall('/api/admin/analytics', { method: 'GET' }, token),
  
  uploadStudents: (file: File, token?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_URL}/api/admin/bulk-upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    }).then(res => res.json());
  },
};

/**
 * Recommendations API
 */
export const recommendationsAPI = {
  get: (data: any, token?: string) =>
    apiCall('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token),
};
