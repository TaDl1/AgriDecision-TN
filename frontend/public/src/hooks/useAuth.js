/**
 * Authentication hook
 */
import { useState, useEffect } from 'react';
import api from '../services/api';
import storage from '../services/storage';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const initAuth = async () => {
      try {
        const token = api.getToken();
        const savedUser = storage.getUser();

        if (token && savedUser) {
          setUser(savedUser);
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (phone, password) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.login(phone, password);

      if (response.user) {
        setUser(response.user);
        storage.saveUser(response.user);
      }

      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.register(userData);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    storage.clearUser();
    setUser(null);
  };

  const updateUser = (userData) => {
    setUser(userData);
    storage.saveUser(userData);
  };

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };
};