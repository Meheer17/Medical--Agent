'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, UserRole } from '@/types';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  signup: (email: string, username: string, pass: string, fullName: string, role: UserRole) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('cliniq_token');
    const storedUser = localStorage.getItem('cliniq_user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem('cliniq_user');
      }
      // Verify token with backend
      api.auth.getProfile()
        .then((fetchedUser) => {
          setUser(fetchedUser);
          localStorage.setItem('cliniq_user', JSON.stringify(fetchedUser));
        })
        .catch(() => {
          // Token expired or invalid
          localStorage.removeItem('cliniq_token');
          localStorage.removeItem('cliniq_user');
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.auth.login({ email, password: pass });
      setToken(res.access_token);
      setUser(res.user);
      localStorage.setItem('cliniq_token', res.access_token);
      localStorage.setItem('cliniq_user', JSON.stringify(res.user));

      // Redirect based on role
      if (res.user.role === 'PATIENT') router.push('/dashboard/patient');
      else if (res.user.role === 'DOCTOR') router.push('/dashboard/doctor');
      else if (res.user.role === 'LAB') router.push('/dashboard/lab');
      else router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (
    email: string,
    username: string,
    pass: string,
    fullName: string,
    role: UserRole
  ) => {
    setIsLoading(true);
    try {
      const res = await api.auth.signup({
        email,
        username,
        password: pass,
        full_name: fullName,
        role,
      });
      setToken(res.access_token);
      setUser(res.user);
      localStorage.setItem('cliniq_token', res.access_token);
      localStorage.setItem('cliniq_user', JSON.stringify(res.user));

      if (res.user.role === 'PATIENT') router.push('/dashboard/patient');
      else if (res.user.role === 'DOCTOR') router.push('/dashboard/doctor');
      else if (res.user.role === 'LAB') router.push('/dashboard/lab');
      else router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('cliniq_token');
    localStorage.removeItem('cliniq_user');
    setToken(null);
    setUser(null);
    router.push('/');
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const updated = await api.auth.getProfile();
      setUser(updated);
      localStorage.setItem('cliniq_user', JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to refresh user', e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
