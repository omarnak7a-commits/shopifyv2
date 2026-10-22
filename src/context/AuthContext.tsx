import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';
import type { AppUser, UserRole } from '../types';
import { apiLogin, apiRegister, apiGetMe, getTokens, saveTokens, clearTokens } from '../services/api';

interface AuthContextValue {
  user: AppUser | null;
  loading: boolean;
  signUp: (email: string, password: string, role: UserRole, displayName: string) => Promise<{ error: string | null }>;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => void;
  resetPassword: (email: string) => Promise<{ error: string | null }>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tokens = getTokens();
    if (!tokens) {
      setLoading(false);
      return;
    }
    apiGetMe()
      .then((u) => setUser(u))
      .catch(() => {
        clearTokens();
      })
      .finally(() => setLoading(false));
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    try {
      const resp = await apiLogin(email, password);
      setUser(resp.user);
      return { error: null };
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Sign in failed.';
      return { error: msg };
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string, role: UserRole, displayName: string) => {
    try {
      const resp = await apiRegister(email, password, role, displayName);
      setUser(resp.user);
      return { error: null };
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Registration failed.';
      return { error: msg };
    }
  }, []);

  const signOut = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const resetPassword = useCallback(async (_email: string) => {
    return { error: null };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signUp, signIn, signOut, resetPassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
