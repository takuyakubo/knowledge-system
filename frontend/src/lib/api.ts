import axios from 'axios';

// APIのベースURLを環境変数から取得、デフォルトはローカル環境
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Axiosインスタンスの作成
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（認証トークンの自動付与）
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター（トークンリフレッシュ対応）
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);

          // 元のリクエストを新しいトークンで再実行
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // リフレッシュに失敗したらログアウト
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API エンドポイント
export const authAPI = {
  register: (data: { email: string; password: string; display_name?: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  logout: () => api.post('/auth/logout'),

  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),

  me: () => api.get('/auth/me'),

  updateProfile: (data: { display_name?: string }) =>
    api.put('/auth/me', data),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.put('/auth/change-password', data),

  verifyEmail: (token: string) =>
    api.post('/auth/verify-email', { token }),

  requestPasswordReset: (email: string) =>
    api.post('/auth/request-password-reset', { email }),

  resetPassword: (data: { token: string; new_password: string }) =>
    api.post('/auth/reset-password', data),
};

export const articleAPI = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api.get('/articles/', { params }),

  get: (id: number) =>
    api.get(`/articles/${id}`),

  create: (data: {
    title: string;
    content: string;
    summary?: string;
    category_id?: number;
    tags?: string[];
  }) => api.post('/articles/', data),

  update: (id: number, data: {
    title?: string;
    content?: string;
    summary?: string;
    category_id?: number;
    tags?: string[];
  }) => api.put(`/articles/${id}`, data),

  delete: (id: number) =>
    api.delete(`/articles/${id}`),
};

export const paperAPI = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api.get('/papers/', { params }),

  get: (id: number) =>
    api.get(`/papers/${id}`),

  create: (data: {
    title: string;
    authors: string[];
    abstract?: string;
    publication_year?: number;
    doi?: string;
    url?: string;
    journal?: string;
    conference?: string;
    file_id?: number;
    category_id?: number;
    tags?: string[];
  }) => api.post('/papers/', data),

  update: (id: number, data: {
    title?: string;
    authors?: string[];
    abstract?: string;
    publication_year?: number;
    doi?: string;
    url?: string;
    journal?: string;
    conference?: string;
    file_id?: number;
    category_id?: number;
    tags?: string[];
  }) => api.put(`/papers/${id}`, data),

  delete: (id: number) =>
    api.delete(`/papers/${id}`),
};

export const categoryAPI = {
  list: () => api.get('/categories/'),

  get: (id: number) =>
    api.get(`/categories/${id}`),

  create: (data: { name: string; description?: string; parent_id?: number }) =>
    api.post('/categories/', data),

  update: (id: number, data: { name?: string; description?: string; parent_id?: number }) =>
    api.put(`/categories/${id}`, data),

  delete: (id: number) =>
    api.delete(`/categories/${id}`),
};

export const tagAPI = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api.get('/tags/', { params }),

  popular: () =>
    api.get('/tags/popular'),

  get: (id: number) =>
    api.get(`/tags/${id}`),

  create: (data: { name: string; description?: string }) =>
    api.post('/tags/', data),

  update: (id: number, data: { name?: string; description?: string }) =>
    api.put(`/tags/${id}`, data),

  delete: (id: number) =>
    api.delete(`/tags/${id}`),
};

export const fileAPI = {
  upload: (file: File, purpose?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (purpose) {
      formData.append('purpose', purpose);
    }

    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  get: (id: number) =>
    api.get(`/files/${id}`),

  download: (id: number) =>
    api.get(`/files/${id}/download`, { responseType: 'blob' }),

  delete: (id: number) =>
    api.delete(`/files/${id}`),
};
