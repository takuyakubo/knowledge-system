import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authAPI } from '../lib/api';

interface User {
  id: number;
  email: string;
  display_name?: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初期ロード時にユーザー情報を取得
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await authAPI.me();
          setUser(response.data);
        } catch (error) {
          // トークンが無効な場合はクリア
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authAPI.login({ email, password });
    const { access_token, refresh_token } = response.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // ユーザー情報を取得
    const userResponse = await authAPI.me();
    setUser(userResponse.data);
  };

  const register = async (email: string, password: string, displayName?: string) => {
    const response = await authAPI.register({
      email,
      password,
      full_name: displayName,
    });
    const user = response.data;

    // 登録後にログインして認証トークンを取得
    await login(email, password);
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // ログアウトAPIが失敗してもローカルのトークンは削除
      console.error('Logout API failed:', error);
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const refreshToken = async () => {
    const currentRefreshToken = localStorage.getItem('refresh_token');
    if (!currentRefreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await authAPI.refresh(currentRefreshToken);
    const { access_token, refresh_token } = response.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
