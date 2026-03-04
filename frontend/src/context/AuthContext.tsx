import { createContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { UserResponse } from '../types/api';
import { getToken, setToken as storeToken, removeToken } from '../api/client';
import * as authApi from '../api/auth';

export interface AuthContextValue {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; nombre: string; telefono?: string }) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore session on mount
  useEffect(() => {
    const token = getToken();
    if (token) {
      const storedUser = localStorage.getItem('budget_user');
      if (storedUser) {
        try { setUser(JSON.parse(storedUser)); } catch { /* ignore */ }
      }
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authApi.login({ email, password });
      storeToken(res.token);
      setUser(res.user);
      localStorage.setItem('budget_user', JSON.stringify(res.user));
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al iniciar sesion';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (data: { email: string; password: string; nombre: string; telefono?: string }) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authApi.register(data);
      storeToken(res.token);
      setUser(res.user);
      localStorage.setItem('budget_user', JSON.stringify(res.user));
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al registrarse';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    removeToken();
    localStorage.removeItem('budget_user');
    setUser(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
