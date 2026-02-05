import { useState, useEffect, createContext, useContext } from 'react';
import { usersApi } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Load current user and available users
    Promise.all([
      usersApi.getCurrentUser().catch(() => ({ data: { user: null } })),
      usersApi.list().catch(() => ({ data: { results: [] } })),
    ]).then(([currentUserRes, usersRes]) => {
      if (currentUserRes.data && currentUserRes.data.id) {
        setUser(currentUserRes.data);
      }
      // Ensure users is always an array
      const userData = usersRes.data.results || usersRes.data || [];
      setUsers(Array.isArray(userData) ? userData : []);
      setLoading(false);
    }).catch((error) => {
      console.error('Failed to load initial data:', error);
      setUsers([]);
      setLoading(false);
    });
  }, []);

  const login = async (username) => {
    try {
      const response = await usersApi.login(username);
      setUser(response.data);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = async () => {
    try {
      await usersApi.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value = {
    user,
    users,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
