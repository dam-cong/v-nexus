import React, { createContext, useContext, useState, useEffect } from 'react';
import { getToken, setToken, removeToken, getUser, setUser } from '../api';

const AuthContext = createContext(null);

const OFFLINE_DEMO_USER = {
  id: 0,
  name: 'Học sinh (offline)',
  email: 'offline@vnexus.vn',
  role: 'hoc_sinh',
};

export function AuthProvider({ children }) {
  const [user, setUserData] = useState(() => getUser());
  const [token, setTokenState] = useState(() => getToken());
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ""}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Đăng nhập thất bại");
      }
      const data = await res.json();
      setToken(data.access_token);
      setUser(data.user);
      setTokenState(data.access_token);
      setUserData(data.user);
      return data.user;
    } finally {
      setLoading(false);
    }
  };

  const loginOfflineDemo = () => {
    const demoToken = 'offline-demo-token';
    setToken(demoToken);
    setUser(OFFLINE_DEMO_USER);
    setTokenState(demoToken);
    setUserData(OFFLINE_DEMO_USER);
  };

  const logout = () => {
    removeToken();
    setTokenState(null);
    setUserData(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    loginOfflineDemo,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
