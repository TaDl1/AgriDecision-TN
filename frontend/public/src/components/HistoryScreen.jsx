import React, { useState, useEffect, useMemo } from 'react';
import {
  ArrowLeft, Calendar, ThermometerSun, Loader, Trash2, Edit2, X, Save,
  AlertTriangle, Filter, ChevronDown, Info, Sprout, CloudRain, Sun, Leaf, ArrowRight
} from 'lucide-react';
import api from '../services/api';
import { CROP_ICONS } from '../utils/constants';
import { formatDate } from '../utils/helpers';
import LoadingSpinner from './LoadingSpinner';
import VoiceRecorder from './VoiceRecorder';

const EditModal = ({ decision, onClose, onSave }) => {
  const [outcome, setOutcome] = useState(decision.outcome || 'success');
  const [yieldKg, setYieldKg] = useState(decision.yield_kg || '');
  const [revenue, setRevenue] = useState(decision.revenue_tnd || '');
  const [notes, setNotes] = useState(decision.notes || '');
  const [actualAction, setActualAction] = useState(decision.actual_action || 'planted_now');
  const [loading, setLoading] = useState(false);
  const [voicePulse, setVoicePulse] = useState(null);
  const handleVoiceResult = (result, field) => {
    console.log(`🎙️ History Voice Input for ${field}:`, result);
    if (result?.numbers?.length > 0) {
      const num = result.numbers[0];
      console.log(`✅ Applying number ${num} to ${field}`);
      if (field === 'yield') setYieldKg(num.toString());
      if (field === 'revenue') setRevenue(num.toString());
      setVoicePulse(field);
      setTimeout(() => setVoicePulse(null), 1000);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.updateAdviceAction(decision.id, { actual_action: actualAction });
      await api.updateDecisionOutcome(decision.id, {
        outcome,
        yield_kg: parseFloat(yieldKg) || 0,
        revenue_tnd: parseFloat(revenue) || 0,
        notes
      });
      onSave();
    } catch (error) {
      console.error("Failed to save:", error);
      alert("Failed to save changes: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-3xl w-full max-w-lg p-8 shadow-2xl overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-gray-900">Refine Record</h3>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors"><X size={24} className="text-gray-400" /></button>
        </div>

        <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2 scrollbar-hide">
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
            <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest mb-4">Action Taken</h4>
            <div className="grid grid-cols-1 gap-3">
              {[
                { val: 'planted_now', label: 'Planted Now', emoji: '🌱' },
                { val: 'waited', label: 'Waited', emoji: '⏱️' },
                { val: 'not_planted', label: 'Did Not Plant', emoji: '❌' }
              ].map(opt => (
                <button
                  key={opt.val}
                  onClick={() => setActualAction(opt.val)}
                  className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${actualAction === opt.val
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-900 shadow-sm'
                    : 'bg-white border-slate-100 text-slate-600 hover:border-slate-200'
                    }`}
                >
                  <span className="font-semibold">{opt.emoji} {opt.label}</span>
                  {actualAction === opt.val && <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center"><X size={12} className="text-white rotate-45" /></div>}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
            <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest mb-4">Harvest Outcome</h4>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Status</label>
                <select
                  value={outcome}
                  onChange={(e) => setOutcome(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-200 text-sm font-medium bg-white focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="success">Success</option>
                  <option value="failure">Failure</option>
                </select>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-xs font-bold text-slate-500 uppercase">Yield (kg)</label>
                  <VoiceRecorder variant="icon" onResult={(res) => handleVoiceResult(res, 'yield')} />
                </div>
                <input
                  type="number"
                  value={yieldKg}
                  onChange={(e) => setYieldKg(e.target.value)}
                  className={`w-full p-3 rounded-xl border text-sm font-medium bg-white focus:ring-2 focus:ring-emerald-500 outline-none transition-all ${voicePulse === 'yield' ? 'border-emerald-500 ring-4 ring-emerald-100 scale-105' : 'border-slate-200'
                    }`}
                  placeholder="0.0"
                />
              </div>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-bold text-slate-500 uppercase">Revenue (TND)</label>
                <VoiceRecorder variant="icon" onResult={(res) => handleVoiceResult(res, 'revenue')} />
              </div>
              <input
                type="number"
                value={revenue}
                onChange={(e) => setRevenue(e.target.value)}
                className={`w-full p-3 rounded-xl border text-sm font-medium bg-white focus:ring-2 focus:ring-emerald-500 outline-none transition-all ${voicePulse === 'revenue' ? 'border-emerald-500 ring-4 ring-emerald-100 scale-105' : 'border-slate-200'
                  }`}
                placeholder="0.0"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full p-3 rounded-xl border border-slate-200 text-sm font-medium h-24 focus:ring-2 focus:ring-emerald-500 outline-none bg-white"
                placeholder="Describe your observations..."
              />
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 text-slate-500 font-bold hover:bg-slate-50 rounded-2xl transition-colors border-2 border-slate-100"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex-[2] px-6 py-3 bg-emerald-600 text-white font-bold rounded-2xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 flex items-center justify-center gap-2"
          >
            {loading ? <Loader size={18} className="animate-spin" /> : <Save size={20} />}
            Confirm Changes
          </button>
        </div>
      </div>
    </div>
  );
};

const EducationalEmptyState = ({ crop, period, type, onClear }) => {
  const isCropOnly = type === 'crop';
  const isPeriodOnly = type === 'period';
  const isBoth = type === 'both';

  return (
    <div className="animate-fade-in py-12 px-6 bg-white rounded-[2.5rem] border-2 border-slate-100 shadow-sm overflow-hidden flex flex-col md:flex-row gap-8 items-center text-left">
      <div className="flex-1 space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full font-bold text-sm">
          <Info size={16} />
          Agricultural Insight
        </div>

        <h2 className="text-3xl font-extrabold text-slate-900 leading-tight">
          {isCropOnly && `Exploring ${crop.name}?`}
          {isPeriodOnly && `Planning for ${period.name}?`}
          {isBoth && `${crop.name} in ${period.name}`}
        </h2>

        <p className="text-slate-600 text-lg leading-relaxed">
          {isCropOnly && `You haven't recorded decisions for ${crop.name} yet. In your region, this crop typically thrives with moderate irrigation and stable temperatures.`}
          {isPeriodOnly && `You have no planting records for ${period.name}. This is usually a busy time for Tunisian farmers focusing on maintaining established soil moisture.`}
          {isBoth && `Growing ${crop.name} during ${period.name} is a strategic choice. Note that ${period.name} weather might require specific irrigation adjustments for ${crop.name}.`}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <h4 className="font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Sprout size={18} className="text-emerald-500" />
              Optimal Window
            </h4>
            <p className="text-sm text-slate-500">March - April is ideal for highest yields.</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <h4 className="font-bold text-slate-900 mb-2 flex items-center gap-2">
              <ThermometerSun size={18} className="text-orange-500" />
              Climate Fact
            </h4>
            <p className="text-sm text-slate-500">Requires minimum 15°C soil temperature.</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 pt-4">
          <button className="px-6 py-3 bg-emerald-600 text-white font-bold rounded-2xl hover:bg-emerald-700 transition-all flex items-center gap-2 group">
            Plan first {crop?.name || 'planting'}
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={onClear}
            className="px-6 py-3 bg-white text-slate-600 font-bold rounded-2xl hover:bg-slate-50 transition-all border-2 border-slate-100"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <div className="hidden md:block w-72 h-72 bg-gradient-to-br from-emerald-100 to-blue-100 rounded-[3rem] relative overflow-hidden flex-shrink-0">
        <div className="absolute inset-0 flex items-center justify-center text-9xl opacity-40">
          {isCropOnly ? (CROP_ICONS[crop.name] || '🌱') : (isPeriodOnly ? '📅' : '🔬')}
        </div>
      </div>
    </div>
  );
};

const HistoryScreen = ({ onBack }) => {
  const [history, setHistory] = useState([]);
  const [filtersData, setFiltersData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [offset, setOffset] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Filters state
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [periodView, setPeriodView] = useState('month'); // month, period, season
  const [selectedPeriod, setSelectedPeriod] = useState(null);

  // Edit/Delete state
  const [editingItem, setEditingItem] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const limit = 20;

  useEffect(() => {
    fetchFilters();
  }, []);

  useEffect(() => {
    loadHistory();
  }, [refreshTrigger, selectedCrop, selectedPeriod]);

  const fetchFilters = async () => {
    try {
      const data = await api.getHistoryFilters();
      setFiltersData(data);
    } catch (err) {
      console.error("Failed to fetch filters:", err);
    }
  };

  const loadHistory = async (loadMore = false) => {
    try {
      if (loadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }

      const currentOffset = loadMore ? offset : 0;

      const activeFilters = {};
      if (selectedCrop) activeFilters.crop_id = selectedCrop.id;
      if (selectedPeriod) {
        activeFilters.period_type = periodView;
        activeFilters.period_value = selectedPeriod.value || selectedPeriod.id;
      }

      const response = await api.getDecisionHistory(limit, currentOffset, activeFilters);

      const newDecisions = response.decisions || [];

      if (loadMore) {
        setHistory((prev) => [...prev, ...newDecisions]);
        setOffset(currentOffset + limit);
      } else {
        setHistory(newDecisions);
        setOffset(limit);
      }

      setTotalCount(response.total);
      setHasMore(newDecisions.length === limit);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteDecision(id);
      setDeletingId(null);
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const getRecommendationBadge = (recommendation) => {
    const badges = {
      PLANT_NOW: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      WAIT: 'bg-amber-100 text-amber-800 border-amber-200',
      NOT_RECOMMENDED: 'bg-rose-100 text-rose-800 border-rose-200',
    };

    const labels = {
      PLANT_NOW: 'PLANT NOW',
      WAIT: 'WAIT',
      NOT_RECOMMENDED: 'STAY CAUTIOUS',
    };

    const icons = {
      PLANT_NOW: <Sprout size={14} />,
      WAIT: <Calendar size={14} />,
      NOT_RECOMMENDED: <AlertTriangle size={14} />,
    };

    return (
      <span className={`px-4 py-1.5 rounded-full font-extrabold text-[10px] tracking-widest border flex items-center gap-2 uppercase ${badges[recommendation]}`}>
        {icons[recommendation]}
        {labels[recommendation]}
      </span>
    );
  };

  const handleClearFilters = () => {
    setSelectedCrop(null);
    setSelectedPeriod(null);
  };

  const renderFilterDropdowns = () => {
    if (!filtersData) return null;

    return (
      <div className="flex flex-col md:flex-row gap-4 mb-10 overflow-visible z-40 relative">
        {/* CROP FILTER */}
        <div className="flex-1 relative group">
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 ml-4">Filter by Crop</label>
          <div className="relative">
            <select
              value={selectedCrop?.id || ''}
              onChange={(e) => {
                const crop = filtersData.crops.find(c => c.id === parseInt(e.target.value));
                setSelectedCrop(crop || null);
              }}
              className="w-full h-16 pl-6 pr-12 bg-white rounded-3xl border-2 border-slate-100 shadow-sm appearance-none outline-none focus:border-emerald-500 transition-all font-bold text-slate-700 text-sm"
            >
              <option value="">All Crops</option>
              {filtersData.crops.map(crop => (
                <option key={crop.id} value={crop.id}>
                  {crop.name} ({crop.count})
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={20} />
          </div>
        </div>

        {/* PERIOD FILTER */}
        <div className="flex-1 relative">
          <div className="flex justify-between items-center mb-2 ml-4 mr-4">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Filter by Period</label>
            <div className="flex gap-2">
              {['month', 'period', 'season'].map(type => (
                <button
                  key={type}
                  onClick={() => {
                    setPeriodView(type);
                    setSelectedPeriod(null);
                  }}
                  className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-md transition-all ${periodView === type ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-400 hover:bg-slate-200'
                    }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
          <div className="relative">
            <select
              value={selectedPeriod ? (selectedPeriod.value || selectedPeriod.id) : ''}
              onChange={(e) => {
                const val = e.target.value;
                let period = null;
                if (periodView === 'month') period = filtersData.months.find(m => m.value.toString() === val);
                else if (periodView === 'period') period = filtersData.periods.find(p => p.id === val);
                else period = filtersData.seasons.find(s => s.value === val);
                setSelectedPeriod(period || null);
              }}
              className="w-full h-16 pl-6 pr-12 bg-white rounded-3xl border-2 border-slate-100 shadow-sm appearance-none outline-none focus:border-emerald-500 transition-all font-bold text-slate-700 text-sm"
            >
              <option value="">All Time</option>
              {periodView === 'month' && filtersData.months.map(m => (
                <option key={m.value} value={m.value}>{m.name} ({m.count})</option>
              ))}
              {periodView === 'period' && filtersData.periods.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.count})</option>
              ))}
              {periodView === 'season' && filtersData.seasons.map(s => (
                <option key={s.value} value={s.value}>{s.name} ({s.count})</option>
              ))}
            </select>
            <ChevronDown className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={20} />
          </div>
        </div>
      </div>
    );
  };

  const activeFiltersTags = () => {
    if (!selectedCrop && !selectedPeriod) return null;
    return (
      <div className="flex flex-wrap gap-2 mb-8 items-center">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter mr-2">Applied:</span>
        {selectedCrop && (
          <span className="bg-emerald-50 text-emerald-700 px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-2 border border-emerald-100">
            {selectedCrop.name}
            <button onClick={() => setSelectedCrop(null)} className="hover:text-emerald-900"><X size={14} /></button>
          </span>
        )}
        {selectedPeriod && (
          <span className="bg-blue-50 text-blue-700 px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-2 border border-blue-100">
            {selectedPeriod.name}
            <button onClick={() => setSelectedPeriod(null)} className="hover:text-blue-900"><X size={14} /></button>
          </span>
        )}
        {(selectedCrop || selectedPeriod) && (
          <button
            onClick={handleClearFilters}
            className="text-xs font-bold text-rose-500 hover:underline ml-2"
          >
            Clear All
          </button>
        )}
      </div>
    );
  };

  if (loading && history.length === 0 && !selectedCrop && !selectedPeriod) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <LoadingSpinner size="large" message="Authenticating History..." />
      </div>
    );
  }

  return (
    <div className="w-full space-y-10 pb-20 px-4 sm:px-6 lg:px-8 pt-10">
      {/* Header Area */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 mb-12">
        <div className="space-y-2">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 text-slate-400 hover:text-emerald-600 font-bold text-xs uppercase tracking-widest transition-all mb-4"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <h1 className="text-5xl font-black text-slate-900 tracking-tight">Decision Index</h1>
          <p className="text-slate-500 font-medium">Reviewing {totalCount} total entries in your personal ledger</p>
        </div>

        <div className="flex items-center gap-4 bg-white p-2 rounded-[2rem] shadow-lg shadow-slate-100 border border-slate-100">
          <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
            <Calendar size={28} />
          </div>
          <div className="pr-8">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Showing Results</p>
            <p className="text-xl font-black text-slate-900">{history.length} / {totalCount}</p>
          </div>
        </div>
      </div>

      {/* FILTER SYSTEM */}
      <div className="animate-slide-up">
        {renderFilterDropdowns()}
        {activeFiltersTags()}
      </div>

      {history.length === 0 ? (
        <EducationalEmptyState
          crop={selectedCrop}
          period={selectedPeriod}
          type={selectedCrop && selectedPeriod ? 'both' : (selectedCrop ? 'crop' : (selectedPeriod ? 'period' : 'none'))}
          onClear={handleClearFilters}
        />
      ) : (
        <div className="animate-fade-in grid gap-6">
          {history.map((item, idx) => (
            <div
              key={item.id}
              className={`border-2 border-slate-100 rounded-[2.5rem] p-8 hover:border-emerald-200 hover:shadow-2xl hover:shadow-emerald-50/50 transition-all duration-300 bg-white relative group animate-slide-up`}
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              {/* Action Buttons */}
              <div className="absolute top-6 right-8 flex gap-3 opacity-0 group-hover:opacity-100 transition-all transform translate-x-4 group-hover:translate-x-0 z-20">
                <button
                  onClick={() => setEditingItem(item)}
                  className="w-10 h-10 bg-white border-2 border-slate-200 rounded-full flex items-center justify-center hover:bg-emerald-50 hover:border-emerald-500 text-emerald-600 shadow-lg transition-all"
                  title="Edit details"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  onClick={() => setDeletingId(item.id)}
                  className="w-10 h-10 bg-white border-2 border-slate-200 rounded-full flex items-center justify-center hover:bg-rose-50 hover:border-rose-500 text-rose-600 shadow-lg transition-all"
                  title="Delete decision"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              {/* Delete Confirmation Overlay */}
              {deletingId === item.id && (
                <div className="absolute inset-0 bg-white/95 z-10 flex flex-col items-center justify-center rounded-[2.5rem] backdrop-blur-sm animate-fade-in">
                  <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mb-4">
                    <AlertTriangle size={32} />
                  </div>
                  <h4 className="font-black text-xl text-slate-900 mb-1 tracking-tight">Erase this entry?</h4>
                  <p className="text-sm text-slate-500 mb-6 font-medium">This record will be permanently deleted from history.</p>
                  <div className="flex gap-4">
                    <button
                      onClick={() => setDeletingId(null)}
                      className="px-6 py-2.5 rounded-2xl text-slate-500 hover:bg-slate-100 font-bold transition-all border-2 border-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="px-6 py-2.5 rounded-2xl bg-rose-600 text-white font-bold hover:bg-rose-700 shadow-lg shadow-rose-100 transition-all"
                    >
                      Delete Forever
                    </button>
                  </div>
                </div>
              )}

              <div className="flex flex-col lg:flex-row gap-10">
                {/* Left Section: Identity & Recommendation */}
                <div className="lg:w-1/3 space-y-6">
                  <div className="flex items-center gap-6">
                    <div className="w-20 h-20 bg-emerald-50 rounded-3xl flex items-center justify-center text-5xl shadow-inner">
                      {CROP_ICONS[item.crop_name] || '🌱'}
                    </div>
                    <div>
                      <h3 className="font-black text-3xl text-slate-900 tracking-tighter leading-none mb-2">{item.crop_name}</h3>
                      <div className="flex items-center gap-2 text-slate-400 font-bold text-xs uppercase tracking-widest">
                        <Calendar size={14} className="text-emerald-500" />
                        {formatDate(item.date)}
                      </div>
                    </div>
                  </div>

                  <div className="pt-2">
                    {getRecommendationBadge(item.recommendation)}
                  </div>

                  {(item.seedling_cost_tnd || item.market_price_tnd) && (
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-2">
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-3">
                        <div className="w-1 h-1 bg-emerald-500 rounded-full"></div>
                        Financial Baseline
                      </p>
                      <div className="grid grid-cols-2 gap-2">
                        {item.seedling_cost_tnd && (
                          <div className="text-xs">
                            <span className="text-slate-400 block mb-0.5">Seedlings</span>
                            <span className="font-bold text-slate-700">{item.seedling_cost_tnd} TND</span>
                          </div>
                        )}
                        {item.market_price_tnd && (
                          <div className="text-xs">
                            <span className="text-slate-400 block mb-0.5">Target Price</span>
                            <span className="font-bold text-slate-700">{item.market_price_tnd} TND/kg</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Right Section: Deep Dive */}
                <div className="flex-1">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
                    {/* Prescriptive Insights Card */}
                    <div className="bg-slate-50/50 p-6 rounded-3xl border border-slate-100 flex flex-col">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center text-sm">🤖</div>
                        <h4 className="font-black text-xs text-slate-900 uppercase tracking-widest">Advisor Insight</h4>
                      </div>
                      <p className="text-slate-600 text-sm leading-relaxed mb-4 flex-1 italic">
                        "{item.explanation || 'Optimal environmental conditions detected for this planting window.'}"
                      </p>
                      <div className="flex items-center gap-2 pt-4 border-t border-slate-100">
                        <ThermometerSun size={14} className="text-orange-400" />
                        <span className="text-xs font-bold text-slate-500">Peak Temp: {item.weather_temp || '--'}°C</span>
                      </div>
                    </div>

                    {/* Operational Reality Card */}
                    <div className={`p-6 rounded-3xl border relative flex flex-col ${item.actual_action
                      ? item.advice_status === 'followed'
                        ? 'bg-emerald-50/80 border-emerald-100'
                        : 'bg-amber-50/80 border-amber-100'
                      : 'bg-slate-50 border-slate-100'
                      }`}>
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 bg-white border border-slate-100 rounded-lg flex items-center justify-center text-sm">👤</div>
                        <h4 className="font-black text-xs text-slate-900 uppercase tracking-widest">Your Execution</h4>
                      </div>

                      <div className="flex-1">
                        {item.actual_action ? (
                          <div className="space-y-4">
                            <div>
                              <p className="text-xl font-black text-slate-900 tracking-tight leading-none mb-2 capitalize">
                                {item.actual_action.replace('_', ' ')}
                              </p>
                              <span className={`inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${item.advice_status === 'followed'
                                ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm'
                                : 'bg-amber-500 text-white border-amber-500 shadow-sm'
                                }`}>
                                {item.advice_status} Advice
                              </span>
                            </div>

                            {item.notes && (
                              <p className="text-xs text-slate-500 line-clamp-3 italic">"{item.notes}"</p>
                            )}
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-4">
                            <p className="text-xs font-bold text-slate-400 italic">No outcome recorded yet.</p>
                            <button
                              onClick={() => setEditingItem(item)}
                              className="px-6 py-2 bg-emerald-600 text-white font-black text-[10px] uppercase tracking-widest rounded-full hover:bg-emerald-700 transition-all shadow-md active:scale-95"
                            >
                              + Update Decision
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {hasMore && !loading && history.length > 0 && (
        <div className="mt-12 text-center pb-20">
          <button
            onClick={() => loadHistory(true)}
            disabled={loadingMore}
            className="group px-10 py-4 bg-white hover:bg-slate-900 text-slate-900 hover:text-white border-4 border-slate-900 font-black uppercase tracking-[0.2em] rounded-full transition-all duration-300 flex items-center gap-4 mx-auto"
          >
            {loadingMore ? (
              <>
                <Loader className="animate-spin" size={24} />
                Loading Database...
              </>
            ) : (
              <>
                Discover More Entries
                <ChevronDown size={24} className="group-hover:translate-y-1 transition-transform" />
              </>
            )}
          </button>
        </div>
      )}

      {/* Edit Modal */}
      {editingItem && (
        <EditModal
          decision={editingItem}
          onClose={() => setEditingItem(null)}
          onSave={() => {
            setEditingItem(null);
            setRefreshTrigger(prev => prev + 1);
          }}
        />
      )}
    </div>
  );
};

export default HistoryScreen;
