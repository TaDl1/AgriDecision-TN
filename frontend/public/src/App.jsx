import React, { useState, useEffect } from 'react';
import AuthScreen from './components/AuthScreen';
import DashboardScreen from './components/DashboardScreen';
import AdviceScreen from './components/AdviceScreen';
import HistoryScreen from './components/HistoryScreen';

import AnalyticsScreen from './components/AnalyticsScreen';
import ProfileScreen from './components/ProfileScreen';
import AboutScreen from './components/AboutScreen';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import { useAuth } from './hooks/useAuth';
import api from './services/api';
import './index.css';

import DashboardLayout from './components/DashboardLayout';

function App() {
  const [currentView, setCurrentView] = useState('auth');
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user, login, register, logout, isAuthenticated, updateUser } = useAuth();

  // Listen for URL changes and reset if needed
  useEffect(() => {
    const handlePopState = () => {
      if (!isAuthenticated) {
        setCurrentView('auth');
        setAdvice(null);
        setSelectedCrop(null);
      }
    };

    window.addEventListener('popstate', handlePopState);

    // If user navigates back to root and is not authenticated, reset
    if (window.location.pathname === '/' && !isAuthenticated) {
      setCurrentView('auth');
      setAdvice(null);
      setSelectedCrop(null);
    }

    return () => window.removeEventListener('popstate', handlePopState);
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      loadCrops();
      setCurrentView('dashboard');
    } else {
      // Reset to auth screen when user logs out
      setCurrentView('auth');
      setAdvice(null);
      setSelectedCrop(null);
    }
  }, [isAuthenticated]);

  const loadCrops = async () => {
    try {
      setLoading(true);
      const data = await api.getCrops();
      setCrops(data || []);
    } catch (error) {
      console.error('Failed to load crops:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (phone, password) => {
    try {
      setLoading(true);
      await login(phone, password);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (userData) => {
    try {
      setLoading(true);
      await register(userData);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const handleGetAdvice = async (adviceData, cropId) => {
    setAdvice(adviceData);
    if (cropId) setSelectedCrop(cropId);
    setCurrentView('advice');
  };

  const handleRequestAdvice = async (cropId) => {
    try {
      setLoading(true);
      const result = await api.getAdvice(cropId, user?.governorate);
      if (result) {
        handleGetAdvice(result, cropId);
      }
    } catch (error) {
      console.error('Failed to get advice:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    setAdvice(null);
    setSelectedCrop(null);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    // Clear all state
    setCurrentView('auth');
    setAdvice(null);
    setSelectedCrop(null);
    setCrops([]);
    // Call logout from useAuth hook
    logout();
  };

  if (loading && currentView === 'auth' && !user) {
    return <LoadingSpinner message="Loading AgriDecision-TN..." />;
  }

  return (
    <ErrorBoundary>
      {currentView === 'auth' || !user ? (
        <AuthScreen
          onLogin={handleLogin}
          onRegister={handleRegister}
          loading={loading}
        />
      ) : (
        <DashboardLayout
          user={user}
          activeView={currentView}
          onNavigate={setCurrentView}
          onLogout={handleLogout}
        >
          {currentView === 'dashboard' ? (
            <DashboardScreen
              user={user}
              crops={crops}
              selectedCrop={selectedCrop}
              onSelectCrop={setSelectedCrop}
              onGetAdvice={handleGetAdvice}
              onNavigate={setCurrentView}
              loading={loading}
            />
          ) : currentView === 'advice' ? (
            <AdviceScreen
              advice={advice}
              cropId={selectedCrop}
              crops={crops}
              user={user}
              onBack={handleBackToDashboard}
              onNavigate={setCurrentView}
            />
          ) : currentView === 'history' ? (
            <HistoryScreen
              user={user}
              onBack={handleBackToDashboard}
            />
          ) : currentView === 'analytics' ? (
            <AnalyticsScreen
              user={user}
              onBack={handleBackToDashboard}
            />
          ) : currentView === 'profile' ? (
            <ProfileScreen
              user={user}
              onBack={handleBackToDashboard}
              onLogout={handleLogout}
              onUpdateUser={updateUser}
              onNavigate={setCurrentView}
            />
          ) : currentView === 'about' ? (
            <AboutScreen
              user={user}
              onBack={() => setCurrentView('profile')}
            />
          ) : null}
        </DashboardLayout>
      )}
    </ErrorBoundary>
  );
}

export default App;