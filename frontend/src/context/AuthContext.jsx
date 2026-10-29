import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('transitmatrix_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('transitmatrix_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verify token with backend /api/auth/me on app mount
    const verifyAuth = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('transitmatrix_user', JSON.stringify(res.data));
        } catch (err) {
          console.error('Failed to authenticate token:', err);
          setUser(null);
          setToken(null);
          localStorage.removeItem('transitmatrix_token');
          localStorage.removeItem('transitmatrix_user');
        }
      }
      setLoading(false);
    };

    verifyAuth();
  }, [token]);

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    const { access_token, user_id, role } = res.data;

    setToken(access_token);
    localStorage.setItem('transitmatrix_token', access_token);

    // Fetch full user profile
    try {
      const profileRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      setUser(profileRes.data);
      localStorage.setItem('transitmatrix_user', JSON.stringify(profileRes.data));
      return profileRes.data;
    } catch {
      const fallbackUser = { user_id, username, role };
      setUser(fallbackUser);
      localStorage.setItem('transitmatrix_user', JSON.stringify(fallbackUser));
      return fallbackUser;
    }
  };

  const register = async (userData) => {
    const res = await api.post('/auth/register', userData);
    return res.data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('transitmatrix_token');
    localStorage.removeItem('transitmatrix_user');
  };

  const isAdmin = user?.role === 'ADMIN';
  const isStaff = user?.role === 'STAFF' || user?.role === 'ADMIN';
  const isPassenger = user?.role === 'PASSENGER';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isAdmin,
        isStaff,
        isPassenger,
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
