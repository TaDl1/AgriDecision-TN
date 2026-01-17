/**
 * Authentication screen (Login/Register)
 */
import React, { useState } from 'react';
import { Loader } from 'lucide-react';
import { GOVERNORATES, FARM_TYPES, SOIL_TYPE_OPTIONS } from '../utils/constants';
import { validateRegistrationForm, validateLoginForm } from '../utils/validation';
import Alert from './Alert';

const AuthScreen = ({ onLogin, onRegister }) => {
  const [authMode, setAuthMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [formData, setFormData] = useState({
    phone_number: '',
    password: '',
    first_name: '',
    last_name: '',
    governorate: '',
    farm_type: FARM_TYPES.RAIN_FED,
    soil_type: 'UNKNOWN',
    farm_size_ha: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' });
    setErrors({});

    // Validate form
    const validation =
      authMode === 'register'
        ? validateRegistrationForm(formData)
        : validateLoginForm({ phone: formData.phone_number, password: formData.password });

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setLoading(true);

    try {
      if (authMode === 'register') {
        await onRegister(formData);
        setMessage({
          text: 'Account created successfully! Please login.',
          type: 'success',
        });
        setTimeout(() => {
          setAuthMode('login');
          setFormData((prev) => ({ ...prev, password: '' }));
        }, 1500);
      } else {
        await onLogin(formData.phone_number, formData.password);
      }
    } catch (error) {
      setMessage({
        text: error.message || 'Authentication failed',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Panel - Hero Section (Desktop Only) */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col justify-between p-12 text-white">
        {/* Background Image & Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="/hero-farmer.png"
            alt="Happy Tunisian Farmer"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-emerald-900/90 via-emerald-900/50 to-emerald-900/30 mix-blend-multiply"></div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <span className="text-4xl text-emerald-400">🌾</span>
            <span className="text-2xl font-bold tracking-tight text-white drop-shadow-md">AgriDecision-TN</span>
          </div>
          <h1 className="text-5xl font-bold leading-tight mb-6 drop-shadow-lg">
            Smart Farming <br />
            <span className="text-emerald-300">Decisions</span> for <br />
            Better Yields.
          </h1>
          <p className="text-emerald-50 text-lg max-w-md leading-relaxed drop-shadow-md font-medium">
            Get personalized planting advice powered by real-time weather data and AI analysis tailored for Tunisia's unique climate.
          </p>
        </div>

        <div className="relative z-10 flex gap-6 text-sm text-emerald-100 font-medium drop-shadow-md">
          <span className="flex items-center gap-1">🇹🇳 Tunisia Edition</span>
          <span>•</span>
          <span className="flex items-center gap-1">🤖 AI Powered</span>
          <span>•</span>
          <span className="flex items-center gap-1">🌦️ Real-time Weather</span>
        </div>
      </div>

      {/* Right Panel - Form Section */}
      <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 lg:px-20 xl:px-24 bg-white overflow-y-auto w-full">
        <div className="w-full mx-auto py-12 px-8">
          {/* Mobile Header */}
          <div className="lg:hidden text-center mb-8">
            <div className="text-5xl mb-4 animate-bounce inline-block">🌾</div>
            <h1 className="text-2xl font-bold text-gray-900">AgriDecision-TN</h1>
            <p className="text-sm text-gray-500 mt-2">Smart Farming Solutions</p>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {authMode === 'login' ? 'Welcome back' : 'Create an account'}
            </h2>
            <p className="text-gray-500">
              {authMode === 'login'
                ? 'Enter your phone number to access your farm dashboard.'
                : 'Join thousands of Tunisian farmers making smarter decisions.'}
            </p>
          </div>

          {/* Mode Toggle */}
          <div className="flex p-1 bg-gray-100 rounded-xl mb-8">
            <button
              onClick={() => setAuthMode('login')}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${authMode === 'login'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setAuthMode('register')}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${authMode === 'register'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone Number
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-medium text-sm select-none">
                  +216
                </span>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone_number}
                  onChange={(e) => handleChange('phone_number', e.target.value.replace(/\D/g, ''))}
                  placeholder="12345678"
                  className={`block w-full pl-14 pr-3 py-3 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors sm:text-sm ${errors.phone_number ? 'border-red-300' : 'border-gray-200'
                    }`}
                  required
                  maxLength="8"
                />
              </div>
              {errors.phone_number && (
                <p className="text-red-600 text-xs mt-1">{errors.phone_number}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="••••••••"
                className={`block w-full px-3 py-3 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors sm:text-sm ${errors.password ? 'border-red-300' : 'border-gray-200'
                  }`}
                required
              />
              {errors.password && <p className="text-red-600 text-xs mt-1">{errors.password}</p>}
            </div>

            {authMode === 'register' && (
              <div className="space-y-5 animate-slide-up">
                <div className="space-y-2">
                  <label htmlFor="governorate" className="block text-sm font-medium text-gray-700">
                    Governorate
                  </label>
                  <div className="relative">
                    <select
                      id="governorate"
                      value={formData.governorate}
                      onChange={(e) => handleChange('governorate', e.target.value)}
                      className={`block w-full pl-3 pr-10 py-3 border rounded-xl text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors sm:text-sm appearance-none bg-white ${errors.governorate ? 'border-red-300' : 'border-gray-200'
                        }`}
                      required
                    >
                      <option value="">Select your location...</option>
                      {GOVERNORATES.map((gov) => (
                        <option key={gov} value={gov}>{gov}</option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                  {errors.governorate && (
                    <p className="text-red-600 text-xs mt-1">{errors.governorate}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                      First Name
                    </label>
                    <input
                      id="first_name"
                      type="text"
                      value={formData.first_name || ''}
                      onChange={(e) => handleChange('first_name', e.target.value)}
                      placeholder="Ali"
                      className={`block w-full px-3 py-3 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors sm:text-sm ${errors.first_name ? 'border-red-300' : 'border-gray-200'
                        }`}
                      required
                    />
                    {errors.first_name && (
                      <p className="text-red-600 text-xs mt-1">{errors.first_name}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                      Last Name
                    </label>
                    <input
                      id="last_name"
                      type="text"
                      value={formData.last_name || ''}
                      onChange={(e) => handleChange('last_name', e.target.value)}
                      placeholder="Ben Ahmed"
                      className={`block w-full px-3 py-3 border rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors sm:text-sm ${errors.last_name ? 'border-red-300' : 'border-gray-200'
                        }`}
                      required
                    />
                    {errors.last_name && (
                      <p className="text-red-600 text-xs mt-1">{errors.last_name}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  <span className="block text-sm font-medium text-gray-700">Farm Type</span>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { value: FARM_TYPES.RAIN_FED, label: 'Rain-fed', emoji: '☁️' },
                      { value: FARM_TYPES.IRRIGATED, label: 'Irrigated', emoji: '💧' }
                    ].map((type) => (
                      <label
                        key={type.value}
                        className={`relative flex flex-col items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all ${formData.farm_type === type.value
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : 'border-gray-100 hover:border-gray-200 hover:bg-gray-50 text-gray-600'
                          }`}
                      >
                        <input
                          type="radio"
                          value={type.value}
                          checked={formData.farm_type === type.value}
                          onChange={(e) => handleChange('farm_type', e.target.value)}
                          className="sr-only"
                        />
                        <span className="text-xl mb-1">{type.emoji}</span>
                        <span className="text-sm font-semibold">{type.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <span className="block text-sm font-medium text-gray-700">Farm Details (Optional)</span>
                  <div className="grid grid-cols-1 gap-3">
                    <div>
                      <label htmlFor="soil_type" className="block text-xs font-medium text-gray-600 mb-1">Soil Type</label>
                      <select
                        id="soil_type"
                        value={formData.soil_type}
                        onChange={(e) => handleChange('soil_type', e.target.value)}
                        className="block w-full px-3 py-2 border rounded-lg text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors text-sm border-gray-200 bg-white"
                      >
                        {SOIL_TYPE_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.emoji} {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="farm_size" className="block text-xs font-medium text-gray-600 mb-1">Farm Size (hectares)</label>
                      <input
                        id="farm_size"
                        type="number"
                        step="0.1"
                        min="0"
                        value={formData.farm_size_ha}
                        onChange={(e) => handleChange('farm_size_ha', e.target.value)}
                        placeholder="e.g., 2.5"
                        className="block w-full px-3 py-2 border rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors text-sm border-gray-200"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {message.text && (
              <Alert
                type={message.type}
                message={message.text}
                onClose={() => setMessage({ text: '', type: '' })}
              />
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-3.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader className="animate-spin" size={18} />
                  <span>Processing...</span>
                </span>
              ) : (
                <span>{authMode === 'login' ? 'Sign In' : 'Create Account'}</span>
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-gray-400">
            &copy; 2024 AgriDecision-TN. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;