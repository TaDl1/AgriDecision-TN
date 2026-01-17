/**
 * Main dashboard screen - Optimized for viewport fit
 */
import React, { useState, useEffect } from 'react';
import {
  MapPin,
  History,
  BarChart3,
  LogOut,
  Target,
  Loader,
  LayoutGrid,
  Leaf,
  Apple,
  Bean,
  Calendar,
  Settings
} from 'lucide-react';
import api from '../services/api';
import CropCard from './CropCard';
import LoadingSpinner from './LoadingSpinner';
import Alert from './Alert';
import AgrarianCalendar from './AgrarianCalendar';
import VoiceRecorder from './VoiceRecorder';

const DashboardScreen = ({ user, onLogout, onNavigate, onGetAdvice }) => {
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [activeCategory, setActiveCategory] = useState('vegetable');

  // Financial Settings State
  const [showFinancialModal, setShowFinancialModal] = useState(false);
  const [voicePulse, setVoicePulse] = useState(null); // track which field is pulsing
  const [activeCrop, setActiveCrop] = useState(null);
  const [financialSettings, setFinancialSettings] = useState({
    seedlingCost: localStorage.getItem('seedlingCost') || '',
    marketPrice: localStorage.getItem('marketPrice') || '',
    inputQuantity: '1'
  });

  const [loading, setLoading] = useState(true);
  const [requesting, setRequesting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    loadCrops();
  }, []);

  const handleCalendarCropClick = (cropName) => {
    const normalizedName = cropName.toLowerCase();
    const crop = crops.find(c => c.name.toLowerCase() === normalizedName);
    if (crop) {
      handleSelectCrop(crop.id);
    }
  };

  const loadCrops = async () => {
    try {
      setLoading(true);
      const response = await api.getCrops();
      const cropsArray = Array.isArray(response) ? response : response.crops || [];
      const normalizedCrops = cropsArray.map(crop => ({
        ...crop,
        id: parseInt(crop.id, 10)
      }));
      setCrops(normalizedCrops);
    } catch (error) {
      console.error('Failed to load crops:', error);
      setMessage({ text: 'Failed to load crops.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCrop = (cropId) => {
    const crop = crops.find(c => c.id === cropId);
    setSelectedCrop(cropId);
    setActiveCrop(crop);
    setFinancialSettings(prev => ({ ...prev, inputQuantity: '1' }));
    setShowFinancialModal(true);
  };

  const handleSaveFinancialsAndGetAdvice = async () => {
    if (!financialSettings.seedlingCost || !financialSettings.marketPrice || !financialSettings.inputQuantity) {
      setMessage({ text: 'Please fill in all financial inputs', type: 'error' });
      return;
    }
    localStorage.setItem('seedlingCost', financialSettings.seedlingCost);
    localStorage.setItem('marketPrice', financialSettings.marketPrice);
    setShowFinancialModal(false);
    if (!selectedCrop) return;

    setRequesting(true);
    setMessage({ text: '', type: '' });

    try {
      const result = await api.getAdvice(
        selectedCrop,
        user?.governorate,
        financialSettings.seedlingCost,
        financialSettings.marketPrice,
        financialSettings.inputQuantity
      );
      onGetAdvice(result, selectedCrop);
    } catch (error) {
      setMessage({ text: error.message || 'Failed to get advice.', type: 'error' });
    } finally {
      setRequesting(false);
    }
  };

  const handleVoiceSearch = (result) => {
    console.log('🎙️ Processing Voice Search Result:', result);
    if (result?.crop_name) {
      const crop = crops.find(c => c.name.toLowerCase() === result.crop_name.toLowerCase());
      if (crop) {
        setActiveCategory(crop.category);
        handleSelectCrop(crop.id);
        setMessage({ text: `Found ${crop.name}!`, type: 'success' });
      } else {
        setMessage({ text: `Crop "${result.crop_name}" not found in your list.`, type: 'error' });
      }
    } else {
      setMessage({ text: 'Could not identify the crop. Try speaking the name clearly.', type: 'error' });
    }
  };

  const handleVoiceInput = (result, field) => {
    console.log(`🎙️ Voice Input for ${field}:`, result);
    if (result?.numbers?.length > 0) {
      const num = result.numbers[0];
      console.log(`✅ Applying number ${num} to ${field}`);
      setFinancialSettings(prev => ({ ...prev, [field]: num.toString() }));
      setVoicePulse(field);
      setTimeout(() => setVoicePulse(null), 1000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" message="Loading your field..." />
      </div>
    );
  }

  const categories = [
    { id: 'vegetable', name: 'Vegetables', icon: Leaf, bg: 'bg-emerald-50', text: 'text-emerald-700', active: 'bg-emerald-600 text-white shadow-emerald-200' },
    { id: 'fruit', name: 'Fruits', icon: Apple, bg: 'bg-orange-50', text: 'text-orange-700', active: 'bg-orange-500 text-white shadow-orange-200' },
    { id: 'legume', name: 'Legumes', icon: Bean, bg: 'bg-purple-50', text: 'text-purple-700', active: 'bg-purple-600 text-white shadow-purple-200' }
  ];

  return (
    <div className="h-full flex flex-col space-y-8 w-full pb-10">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl shadow-sm p-8 text-white relative overflow-hidden flex flex-col md:flex-row items-center justify-between min-h-[220px]">
        <div className="relative z-10 max-w-lg">
          <h2 className="text-3xl font-bold mb-2">
            Welcome back, {user.first_name || 'Farmer'}! 👋
          </h2>
          <p className="text-emerald-50 text-lg leading-relaxed">
            Ready to check your crops? Select a crop below to get real-time AI planting advice based on today's weather in {user?.governorate}.
          </p>
          <div className="flex gap-4 mt-6">
            <button onClick={() => onNavigate('history')} className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl backdrop-blur-md transition-all text-sm font-bold">
              <History size={18} /> History
            </button>
            <button onClick={() => onNavigate('analytics')} className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl backdrop-blur-md transition-all text-sm font-bold">
              <BarChart3 size={18} /> Analytics
            </button>
          </div>
        </div>
        <div className="hidden md:block absolute right-0 top-0 bottom-0 w-2/5 z-0">
          <img
            src="/farmer-field.png"
            alt="Farmer walking in field"
            className="w-full h-full object-cover"
            style={{ maskImage: 'linear-gradient(to right, transparent, black 15%)' }}
          />
        </div>
      </div>

      <div className="flex flex-col space-y-8">
        {/* 1. CALENDAR SECTION (Full Width) */}
        <div className="w-full animate-slide-up">
          <AgrarianCalendar
            user={user}
            onCropClick={handleCalendarCropClick}
          />
        </div>

        {/* 2. CROP SELECTION SECTION (Full Width) */}
        <div className="w-full animate-slide-up delay-100">
          <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-6 sm:p-8">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8 overflow-visible">
              <div className="flex items-center gap-6">
                <h3 className="text-lg font-black text-slate-900 uppercase tracking-widest hidden sm:block">Selection</h3>
                <VoiceRecorder variant="search" onResult={handleVoiceSearch} />
              </div>
              <div className="flex bg-slate-50 p-1.5 rounded-2xl border border-slate-100 min-w-max self-start lg:self-auto">
                {categories.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-black text-sm transition-all sm:min-w-[120px] justify-center ${activeCategory === cat.id ? `${cat.active} shadow-lg scale-105` : 'text-slate-500 hover:text-slate-800'}`}
                  >
                    <cat.icon size={18} />
                    <span>{cat.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Category Grid */}
            <div className="min-h-[400px]">
              {crops.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-6 animate-fade-in">
                  {crops.filter(c => c.category === activeCategory).map((crop) => (
                    <CropCard
                      key={crop.id}
                      crop={crop}
                      selected={selectedCrop === crop.id}
                      onClick={handleSelectCrop}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-slate-400 opacity-50 space-y-4">
                  <Loader className="animate-spin" size={32} />
                  <p className="font-bold">Syncing crops...</p>
                </div>
              )}
            </div>

            {message.text && (
              <div className="mt-8 animate-slide-up">
                <Alert
                  type={message.type}
                  message={message.text}
                  onClose={() => setMessage({ text: '', type: '' })}
                  autoClose={true}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Financial Input Modal Implementation */}
      {showFinancialModal && activeCrop && (
        <div className="fixed inset-0 bg-slate-950/80 z-[60] flex items-center justify-center p-4 backdrop-blur-md animate-fade-in">
          <div className="bg-white rounded-[2.5rem] shadow-2xl p-8 max-w-lg w-full animate-scale-in border border-white/20 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
              <span className="text-9xl">{activeCrop.icon}</span>
            </div>

            <div className="relative z-10">
              <div className="flex items-center gap-5 mb-8">
                <div className="w-16 h-16 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-4xl shadow-inner">
                  {activeCrop.icon}
                </div>
                <div>
                  <h3 className="text-3xl font-black text-slate-900 leading-tight">{activeCrop.name}</h3>
                  <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Financial Strategy</p>
                </div>
              </div>

              <div className="space-y-4 mb-8">
                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100 hover:border-emerald-200 transition-colors">
                  <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3">
                    Quantity ({activeCrop.input_type})
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="number"
                      value={financialSettings.inputQuantity}
                      onChange={(e) => setFinancialSettings({ ...financialSettings, inputQuantity: e.target.value })}
                      className={`w-full bg-white border-2 rounded-xl p-3 text-2xl font-black text-slate-800 outline-none transition-all ${voicePulse === 'inputQuantity' ? 'border-emerald-500 bg-emerald-50 ring-4 ring-emerald-100 scale-105' : 'border-slate-200 focus:border-emerald-500'
                        }`}
                    />
                    <VoiceRecorder variant="icon" onResult={(res) => handleVoiceInput(res, 'inputQuantity')} />
                    <div className="px-4 py-2 bg-white rounded-lg border border-slate-200 font-black text-slate-400 min-w-[60px] text-center">
                      {activeCrop.input_type === 'seeds_kg' ? 'kg' : 'unit'}
                    </div>
                  </div>
                </div>

                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-[10px] font-black text-slate-400 uppercase">Cost (TND)</label>
                    <VoiceRecorder variant="icon" onResult={(res) => handleVoiceInput(res, 'seedlingCost')} />
                  </div>
                  <input
                    type="number"
                    value={financialSettings.seedlingCost}
                    onChange={(e) => setFinancialSettings({ ...financialSettings, seedlingCost: e.target.value })}
                    className={`w-full bg-transparent border-b-2 p-1 text-xl font-black outline-none transition-all ${voicePulse === 'seedlingCost' ? 'border-emerald-500 scale-105 bg-emerald-50' : 'border-slate-200 focus:border-emerald-500'
                      }`}
                    placeholder="0.00"
                  />
                </div>
                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-[10px] font-black text-slate-400 uppercase">Price (TND)</label>
                    <VoiceRecorder variant="icon" onResult={(res) => handleVoiceInput(res, 'marketPrice')} />
                  </div>
                  <input
                    type="number"
                    value={financialSettings.marketPrice}
                    onChange={(e) => setFinancialSettings({ ...financialSettings, marketPrice: e.target.value })}
                    className={`w-full bg-transparent border-b-2 p-1 text-xl font-black outline-none transition-all ${voicePulse === 'marketPrice' ? 'border-emerald-500 scale-105 bg-emerald-50' : 'border-slate-200 focus:border-emerald-500'
                      }`}
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowFinancialModal(false)}
                  className="flex-1 py-5 text-slate-400 font-black uppercase tracking-widest hover:text-slate-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveFinancialsAndGetAdvice}
                  className="flex-[2] py-5 bg-slate-900 hover:bg-emerald-600 text-white rounded-2xl transition-all font-black uppercase tracking-widest shadow-xl shadow-slate-200 flex items-center justify-center gap-3 active:scale-95"
                >
                  {requesting ? <Loader className="animate-spin" size={20} /> : (
                    <>Get Analysis <Target size={20} /></>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardScreen;