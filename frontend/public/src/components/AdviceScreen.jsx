/**
 * Advice display screen
 */
import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  AlertTriangle,
  Calendar,
  Cloud,
  Droplets,
  ThermometerSun,
  History,
  Sprout,
  MapPin,
  Volume2,
  TrendingUp,
} from 'lucide-react';
import { CROP_ICONS } from '../utils/constants';
import { getRecommendationStyle, getRiskLevelStyle, formatDate } from '../utils/helpers';
import WeatherCard from './WeatherCard';
import api from '../services/api';
import { getTranslation, getDirection } from '../utils/translations';
import { formatTemp } from '../utils/units';

const AdviceScreen = ({ advice, cropId, crops, onBack, onNavigate, user }) => {
  // Preferences
  const lang = user?.preferences?.language || 'en';
  const units = user?.preferences?.units || 'metric';
  const dir = getDirection(lang);
  const t = (key) => getTranslation(key, lang);

  // Add logging to debug the advice object
  useEffect(() => {
    console.log("AdviceScreen: Received advice object:", advice);
    console.log("AdviceScreen: Received cropId:", cropId);
    console.log("AdviceScreen: Received crops:", crops);
  }, [advice, cropId, crops]);

  if (!advice || !advice.decision) {
    console.error("🛑 AdviceScreen: Missing critical advice data!", advice);
    return (
      <div className="p-8 text-center bg-white rounded-3xl border-2 border-dashed border-slate-300">
        <h2 className="text-xl font-bold text-slate-800 mb-2">{t('failed_load_crops')}</h2>
        <p className="text-slate-500 mb-4">We couldn't load the planting recommendations. Please try again.</p>
        <button onClick={onBack} className="text-emerald-600 font-bold hover:underline flex items-center gap-2 justify-center">
          <ArrowLeft size={16} className={dir === 'rtl' ? 'rotate-180' : ''} /> {t('back_to_dashboard')}
        </button>
      </div>
    );
  }

  const [isListening, setIsListening] = useState(false);
  const [actionRecorded, setActionRecorded] = useState(false);

  const handleRecordAction = async (action) => {
    console.log('📝 Attempting to record action:', action, 'for advice ID:', advice?.id);
    try {
      if (!advice?.id) {
        console.warn("🚫 No advice ID found in advice object:", advice);
        alert("Action could not be recorded: No advice ID session found.");
        return;
      }

      const response = await api.recordAction(advice.id, action);
      console.log('✅ Action recorded successfully:', response);
      setActionRecorded(true);
    } catch (error) {
      console.error("❌ Failed to record action:", error);
      alert(`Failed to record action: ${error.message || 'Please try again.'}`);
    }
  };

  const style = getRecommendationStyle(advice.decision?.action || 'WAIT');
  const selectedCrop = crops.find((c) => c.id === cropId);
  const cropIcon = CROP_ICONS[selectedCrop?.name] || '🌱';
  const riskStyle = advice.period ? getRiskLevelStyle(advice.period.risk) : {};

  const getRecommendationIcon = () => {
    switch (advice.decision?.action) {
      case 'PLANT_NOW':
        return <CheckCircle size={48} />;
      case 'WAIT':
        return <Clock size={48} />;
      default:
        return <AlertTriangle size={48} />;
    }
  };

  const recommendationText = advice.decision.action === 'PLANT_NOW' ? t('plant_now') :
    advice.decision.action === 'WAIT' ? t('wait') :
      advice.decision.action === 'DO_NOT_PLANT' ? t('dont_plant') :
        advice.decision.action.replace('_', ' ');

  return (
    <div className="w-full space-y-8 animate-fade-in" dir={dir}>
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-slate-600 hover:text-emerald-600 font-medium transition-colors"
      >
        <ArrowLeft size={20} className={dir === 'rtl' ? 'rotate-180' : ''} />
        <span>{t('back_to_dashboard')}</span>
      </button>

      <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden animate-fade-in">
        {/* Header */}
        <div
          className={`bg-gradient-to-r ${style.gradient} p-10 text-white text-center relative overflow-hidden`}
        >
          <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>
          <div className="relative z-10">
            <div className="text-8xl mb-4">{cropIcon}</div>
            <h1 className="text-4xl font-bold mb-2">
              {selectedCrop?.name} {t('planting_advice')}
            </h1>
            <p className="text-sm opacity-90 flex items-center justify-center gap-2">
              <MapPin size={16} />
              {advice.period?.name} • {formatDate(new Date().toISOString())}
            </p>
          </div>
        </div>

        <div className="p-8">
          {/* Recommendation Card */}
          <div
            className={`${style.bgColor} border-3 ${style.borderColor} p-8 rounded-2xl mb-6`}
          >
            <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className={style.textColor}>{getRecommendationIcon()}</div>
                <div>
                  <h2 className={`text-3xl font-bold ${style.textColor}`}>
                    {style.emoji} {recommendationText}
                  </h2>
                  {advice.decision.wait_days > 0 && (
                    <p className="text-lg mt-1">
                      {t('wait')} <strong>{advice.decision.wait_days} {t('days')}</strong>
                    </p>
                  )}
                </div>
              </div>
              <div
                className={`px-6 py-3 ${style.bgColor} ${style.borderColor} border-2 rounded-full font-bold ${style.textColor}`}
              >
                {advice.decision.confidence} {t('confidence')}
              </div>
            </div>

            {advice.decision.wait_days > 0 && (
              <div className="bg-white p-4 rounded-xl border-2 border-gray-200">
                <p className="text-gray-700">
                  <strong>{t('best_planting_date')}:</strong>{' '}
                  <span className="text-green-600 font-bold">
                    {formatDate(
                      new Date(
                        Date.now() + advice.decision.wait_days * 86400000
                      ).toISOString()
                    )}
                  </span>
                </p>
              </div>
            )}
          </div>

          {/* AI Explanation */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">💡</div>
                {t('ai_explanation')}
              </h3>
              <button
                onClick={() => {
                  const utterance = new SpeechSynthesisUtterance(advice.explanation);
                  utterance.lang = lang === 'ar' ? 'ar-TN' : lang === 'fr' ? 'fr-FR' : 'en-US';
                  window.speechSynthesis.speak(utterance);
                }}
                className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-full transition-colors"
                title={t('listen')}
              >
                <Volume2 size={18} />
                {t('listen')}
              </button>
            </div>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border-2 border-blue-200">
              <p className="text-gray-800 leading-relaxed text-lg">{advice.explanation}</p>
            </div>
          </div>

          {/* Current Period */}
          {advice.period && (
            <div className="mb-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <Calendar className="text-purple-600" size={28} />
                {t('current_period')}
              </h3>
              <div
                className={`p-6 rounded-xl border-2 ${riskStyle.bg} ${riskStyle.border}`}
              >
                <h4 className="text-xl font-bold mb-2">{advice.period.name}</h4>
                <p className="text-gray-600 mb-3">
                  {advice.period.description || 'Seasonal conditions apply'}
                </p>
                <span
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold ${riskStyle.color} ${riskStyle.bg} ${riskStyle.border} border-2`}
                >
                  {advice.period.risk === 'low' && <CheckCircle size={18} />}
                  {advice.period.risk === 'medium' && <AlertTriangle size={18} />}
                  {advice.period.risk === 'high' && <AlertTriangle size={18} />}
                  {advice.period.risk.toUpperCase()}
                </span>
              </div>
            </div>
          )}

          {/* Weather Forecast */}
          {advice.weather_forecast && advice.weather_forecast.length > 0 && (
            <div className="mb-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <Cloud className="text-blue-600" size={28} />
                {t('weather_outlook')}
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                {advice.weather_forecast.map((day, idx) => (
                  <WeatherCard key={idx} forecast={day} units={units} />
                ))}
              </div>
            </div>
          )}

          {/* Weather Risks */}
          {advice.weather_analysis?.risks && advice.weather_analysis.risks.length > 0 && (
            <div className="mb-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <AlertTriangle className="text-orange-600" size={28} />
                {t('weather_risk')}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {advice.weather_analysis.risks.map((risk, idx) => (
                  <div
                    key={idx}
                    className="bg-orange-50 border-2 border-orange-200 p-4 rounded-xl flex items-center gap-3"
                  >
                    <AlertTriangle className="text-orange-600 flex-shrink-0" size={24} />
                    <div>
                      <span className="font-semibold text-orange-800 block">
                        {risk.type?.replace(/_/g, ' ').toUpperCase() || 'WEATHER RISK'}
                      </span>
                      {risk.date && (
                        <span className="text-sm text-orange-600">{risk.date}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Feedback Loop */}
          <div className="mb-10 bg-slate-900 rounded-[2rem] p-8 text-white shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <Sprout size={120} />
            </div>

            <h3 className="text-2xl font-black mb-2 flex items-center gap-3">
              <CheckCircle className="text-emerald-400" size={32} />
              {t('commit_action')}
            </h3>
            <p className="text-slate-400 mb-8 font-medium max-w-md">
              {t('action_prompt')}
            </p>

            {actionRecorded ? (
              <div className="bg-emerald-500/20 border-2 border-emerald-500/50 rounded-2xl p-6 text-emerald-400 font-bold flex items-center gap-4 animate-scale-in">
                <div className="bg-emerald-500 text-slate-900 p-2 rounded-full">
                  <CheckCircle size={24} />
                </div>
                <div>
                  Action Recorded Successfully!
                  <span className="block text-sm font-medium opacity-80">Reflected in your Compliance Index.</span>
                </div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-3 gap-4">
                <button
                  onClick={() => handleRecordAction('planted_now')}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 px-6 rounded-2xl transition-all shadow-lg hover:-translate-y-1 flex flex-col items-center gap-2"
                >
                  <Sprout size={24} />
                  <span>{t('i_planted_now')}</span>
                </button>
                <button
                  onClick={() => handleRecordAction('waited')}
                  className="bg-amber-600 hover:bg-amber-500 text-white font-bold py-4 px-6 rounded-2xl transition-all shadow-lg hover:-translate-y-1 flex flex-col items-center gap-2"
                >
                  <History size={24} />
                  <span>{t('ill_wait')}</span>
                </button>
                <button
                  onClick={() => handleRecordAction('not_planted')}
                  className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-4 px-6 rounded-2xl transition-all shadow-lg hover:-translate-y-1 flex flex-col items-center gap-2"
                >
                  <AlertTriangle size={24} />
                  <span>{t('i_wont_plant')}</span>
                </button>
              </div>
            )}
          </div>

          {/* Bottom Navigation Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              onClick={onBack}
              className="py-4 bg-white border-2 border-slate-200 text-slate-700 font-bold rounded-2xl hover:bg-slate-50 transition-all flex items-center justify-center gap-2"
            >
              <ArrowLeft size={20} className={dir === 'rtl' ? 'rotate-180' : ''} />
              {t('back_to_dashboard')}
            </button>
            <button
              onClick={() => onNavigate('analytics')}
              className="py-4 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-200"
            >
              <TrendingUp size={20} className={dir === 'rtl' ? 'rotate-180' : ''} />
              {t('view_analytics')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdviceScreen;