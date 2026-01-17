/**
 * Advanced analytics with AI insights
 */
import React, { useState, useEffect } from 'react';
import { ArrowLeft, TrendingUp, Brain, Target, Calendar } from 'lucide-react';
import api from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const AdvancedAnalyticsScreen = ({ user, onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState('');

  useEffect(() => {
    loadAdvancedAnalytics();
  }, []);

  const loadAdvancedAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.getAdvancedAnalytics();
      setAnalytics(data);
      generateInsights(data);
    } catch (error) {
      console.error('Failed to load advanced analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = (data) => {
    // This would typically call an AI service
    const mockInsights = `Based on your farming patterns, we recommend:\n\n1. You have highest success with tomatoes (100% success rate)\n2. Consider planting wheat in October for optimal results\n3. Avoid summer planting for heat-sensitive crops`;
    setInsights(mockInsights);
  };

  if (loading) {
    return <LoadingSpinner message="Generating AI insights..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 p-4">
      <div className="max-w-6xl mx-auto">
        <button onClick={onBack} className="mb-4 btn-secondary flex items-center gap-2">
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>

        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h1 className="text-4xl font-bold mb-8 flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-xl">
              <Brain className="text-purple-600" size={40} />
            </div>
            AI-Powered Insights
          </h1>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-purple-100 to-pink-100 p-6 rounded-2xl border-2 border-purple-200">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Brain size={24} />
                Smart Recommendations
              </h3>
              <pre className="whitespace-pre-wrap font-sans text-gray-800">
                {insights}
              </pre>
            </div>

            <div className="bg-gradient-to-br from-blue-100 to-cyan-100 p-6 rounded-2xl border-2 border-blue-200">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Target size={24} />
                Seasonal Performance
              </h3>
              <p className="text-gray-700">
                Your best planting seasons are Spring and Autumn. Consider adjusting your crop selection based on historical weather patterns in your region.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalyticsScreen;