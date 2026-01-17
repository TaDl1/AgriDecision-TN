/**
 * Analytics dashboard screen
 */
import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  TrendingUp,
  CheckCircle,
  Target,
  AlertTriangle,
  Award,
  DollarSign,
  MapPin,
  Settings,
  ChevronUp,
  ChevronDown,
  RefreshCw,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  Legend
} from 'recharts';
import api from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900/90 backdrop-blur-md border border-white/10 p-4 rounded-xl shadow-2xl text-white">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{label}</p>
        <p className="text-xl font-black">{payload[0].value}% Success</p>
        {payload[0].payload.total && (
          <p className="text-[10px] text-emerald-400 font-medium mt-1">
            Based on {payload[0].payload.total} records
          </p>
        )}
      </div>
    );
  }
  return null;
};

const AnalyticsScreen = ({ onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [personalInsights, setPersonalInsights] = useState(null);
  const [regionalData, setRegionalData] = useState(null);
  const [advancedAnalytics, setAdvancedAnalytics] = useState(null);
  const [smartSummary, setSmartSummary] = useState('');
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [timeframe, setTimeframe] = useState('monthly');

  // Financial Settings State


  useEffect(() => {
    loadAllAnalytics();
  }, [timeframe]);

  const loadAllAnalytics = async () => {
    setLoading(true);
    try {
      const data = await api.getAdvancedAnalytics(timeframe);
      console.log('✅ Analytics loaded:', data);

      if (data) {
        setAnalytics(data); // Personal stats at root
        setAdvancedAnalytics({
          ...data,
          performance_trends_interpretation: data.performance_trends_interpretation // Ensure this is mapped
        });
        setRegionalData(data.regional_data);
        setPersonalInsights(data.personal_insights);
        // Map top-level interpretation for Risks card if available (it might be nested inside result of calculate_rar)
        if (data.risk_avoided_count !== undefined) {
          // We might need to ensure backend sends this at top level or we access it from where it is.
          // Since get_dashboard_data constructs the dict, let's verify where 'interpretation' lands.
          // It lands inside specific internal calls but get_dashboard_data flattens some.
          // Actually, calculate_rar returns a dict, but get_dashboard_data extracts specific fields.
          // I need to update get_dashboard_data in backend to pass the full interpretation too.
          // Wait, I should double check get_dashboard_data in previous step.
        }
        setSmartSummary(data.smart_summary);
      }
    } catch (error) {
      console.error('❌ Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      await api.simulateData();
      await loadAllAnalytics();
    } catch (error) {
      alert("Simulation failed: " + error.message);
    } finally {
      setSimulating(false);
    }
  };



  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <LoadingSpinner size="large" message="Running hyper-local simulations..." />
      </div>
    );
  }

  // Placeholder kept for extremely empty state if needed, but removing blocker as requested
  if (!analytics && !loading) {
    // Only show if truly nothing loaded
    return <div className="p-8 text-center text-slate-500">Failed to load analytics data.</div>;
  }

  const successRate = analytics?.success_rate ? parseFloat(analytics.success_rate) : 0;
  // Map correct key from regional-benchmark endpoint response
  const regionalRate = regionalData?.gsi?.gsi || regionalData?.personal_benchmark?.regional_avg || 0;

  const diffVal = (successRate - (regionalRate || 0));
  const difference = isNaN(diffVal) ? "0.0" : diffVal.toFixed(1);
  const isAboveAvg = parseFloat(difference) > 0;

  return (
    <div className="w-full space-y-10 animate-fade-in relative pb-20">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-slate-500 hover:text-emerald-600 font-bold mb-4 transition-colors"
          >
            <ArrowLeft size={20} /> Portfolio Overview
          </button>
          <h1 className="text-5xl font-black text-slate-900 tracking-tight flex items-center gap-4">
            Intelligence Center
            <span className="text-sm bg-emerald-100 text-emerald-600 px-3 py-1 rounded-full uppercase tracking-tighter">Live Analysis</span>
          </h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={loadAllAnalytics}
            className={`bg-white p-3 rounded-2xl shadow-sm border border-slate-200 text-slate-400 hover:text-emerald-600 transition-colors ${loading ? 'animate-spin' : ''}`}
            title="Refresh Data"
          >
            <RefreshCw size={20} />
          </button>
          <div className="bg-white px-6 py-3 rounded-2xl shadow-sm border border-slate-200 flex items-center gap-3">
            <MapPin size={18} className="text-emerald-500" />
            <span className="font-black text-slate-700">{regionalData?.governorate || 'All Regions'}</span>
          </div>
        </div>
      </header>

      {/* Smart Insight Advisor Section */}
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-blue-100 rounded-[2.5rem] p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-20 transform translate-x-1/4 -translate-y-1/4">
          <Award size={180} />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-2xl text-white">
              <CheckCircle size={24} />
            </div>
            <h2 className="text-2xl font-black text-slate-900">Technical Advisor Summary</h2>
          </div>
          <p className="text-xl font-medium text-slate-700 leading-relaxed max-w-4xl italic">
            "{smartSummary || "Our advisors are processing your recent outcomes. Record more details to unlock specific technical growth strategies for your farm."}"
          </p>
        </div>
      </div>

      {/* SECTION 1: FINANCIAL HEALTH (Risk & Money) */}
      <section className="space-y-6">
        <div className="flex items-center gap-3 border-b border-slate-200 pb-4">
          <div className="bg-orange-100 p-2 rounded-lg text-orange-600">
            <AlertTriangle size={24} />
          </div>
          <h2 className="text-2xl font-black text-slate-800 uppercase tracking-tighter">Financial Health</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Money Saved Card */}
          <div className="bg-gradient-to-br from-purple-600 to-indigo-700 text-white p-8 rounded-[2.5rem] shadow-xl relative overflow-hidden group">
            <div className="relative z-10">
              <div className="text-5xl font-black mb-1 leading-none">{analytics?.savings_tnd || 0} TND</div>
              <div className="text-purple-100 font-bold uppercase text-xs tracking-[0.2em]">Money Saved</div>
              <div className="mt-4 bg-white/10 rounded-lg p-3 border border-white/10">
                <p className="text-[10px] text-purple-200 uppercase font-bold tracking-widest mb-1">ℹ️ What this tells you</p>
                <p className="text-xs text-white leading-relaxed">
                  Value of seedling costs saved by following 'WAIT' or 'NOT_RECOMMENDED' advice during risky conditions.
                </p>
              </div>
            </div>
            <DollarSign className="absolute -right-4 -bottom-4 text-black/10 group-hover:text-black/20 transition-colors" size={160} />
          </div>

          {/* Disasters Avoided Card */}
          <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-100 relative overflow-hidden group">
            <div className="relative z-10">
              <div className="text-6xl font-black text-slate-900 mb-1">{analytics?.risk_avoided_count || 0}</div>
              <div className="text-slate-500 font-bold uppercase text-xs tracking-[0.2em]">Disasters Avoided</div>
              <div className="mt-4 bg-slate-50 rounded-lg p-3 border border-slate-200">
                <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mb-1">ℹ️ What this tells you</p>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Number of times you heeded 'WAIT' or 'NOT_RECOMMENDED' warnings, protecting your investment from bad weather or pest risks.
                </p>
              </div>
              {analytics?.interpretation && (
                <p className="mt-4 text-[10px] text-slate-400 font-bold leading-tight">
                  {analytics.interpretation}
                </p>
              )}
            </div>
            <AlertTriangle className="absolute -right-4 -bottom-4 text-slate-50 group-hover:text-slate-100 transition-colors" size={160} />
          </div>
        </div>

        {/* Financial Advice Footer */}
        <div className="bg-orange-50 border border-orange-100 rounded-2xl p-6">
          <h3 className="text-sm font-black text-orange-800 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="text-xl">💡</span> Financial Strategy
          </h3>
          <ul className="space-y-2">
            {advancedAnalytics?.strategic_advice?.financial?.length > 0 ? (
              advancedAnalytics.strategic_advice.financial.map((tip, i) => (
                <li key={i} className="text-slate-700 text-sm font-medium flex items-start gap-2">
                  <span className="text-orange-400 mt-0.5">•</span>
                  <span dangerouslySetInnerHTML={{ __html: tip.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}></span>
                </li>
              ))
            ) : (
              <li className="text-slate-400 italic text-sm">Record more outcomes to get financial tips.</li>
            )}
          </ul>
        </div>
      </section>

      {/* SECTION 2: CROP PRODUCTION (Success & Choices) */}
      <section className="space-y-6 pt-8">
        <div className="flex items-center gap-3 border-b border-slate-200 pb-4">
          <div className="bg-emerald-100 p-2 rounded-lg text-emerald-600">
            <CheckCircle size={24} />
          </div>
          <h2 className="text-2xl font-black text-slate-800 uppercase tracking-tighter">Crop Production</h2>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Overall Success Rate */}
          <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-100 relative overflow-hidden group">
            <div className="relative z-10">
              {analytics?.total_decisions > 0 ? (
                <>
                  <div className="text-6xl font-black text-slate-900 mb-1">{successRate}%</div>
                  <div className="text-slate-400 font-bold uppercase text-xs tracking-[0.2em]">Overall Success Rate</div>
                  <div className="mt-4 bg-slate-50 rounded-lg p-3 border border-slate-200">
                    <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mb-1">ℹ️ What this tells you</p>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Percentage of your harvests that met expectations.
                    </p>
                  </div>
                </>
              ) : (
                <div className="py-8 text-center text-slate-400">No data yet</div>
              )}
            </div>
          </div>

          {/* Regional Comparison List */}
          <div className="bg-slate-900 rounded-[2.5rem] p-8 text-white shadow-2xl flex flex-col">
            <h3 className="text-xl font-black mb-6 flex items-center justify-between">
              Compare to Neighbors
              <Award className="text-emerald-400" size={20} />
            </h3>
            <div className="flex-1 overflow-auto pr-2 custom-scrollbar space-y-4">
              {regionalData?.top_regional_crops?.map((crop, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
                      #{idx + 1}
                    </div>
                    <div className="font-bold text-white text-sm">{crop.crop_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-black text-emerald-400">{crop.success_rate}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Best Crops Bar Chart */}
          <div className="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 p-8 lg:col-span-2">
            <h3 className="text-xl font-black text-slate-900 mb-2">Which Crops Work Best?</h3>
            <div className="h-[250px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={advancedAnalytics?.crop_accuracy?.chart_data || []} margin={{ bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis
                    dataKey="crop"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: '#64748b', angle: -45, textAnchor: 'end' }}
                    interval={0}
                    tickMargin={5}
                    height={80}
                  />
                  <YAxis hide={true} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Bar dataKey="success_rate" radius={[4, 4, 4, 4]} barSize={30}>
                    {(advancedAnalytics?.crop_accuracy?.chart_data || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#10b981' : '#3b82f6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Production Advice Footer */}
        <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-6">
          <h3 className="text-sm font-black text-emerald-800 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="text-xl">🚜</span> Production Strategy
          </h3>
          <ul className="space-y-2">
            {advancedAnalytics?.strategic_advice?.production?.length > 0 ? (
              advancedAnalytics.strategic_advice.production.map((tip, i) => (
                <li key={i} className="text-slate-700 text-sm font-medium flex items-start gap-2">
                  <span className="text-emerald-400 mt-0.5">•</span>
                  <span dangerouslySetInnerHTML={{ __html: tip.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}></span>
                </li>
              ))
            ) : (
              <li className="text-slate-400 italic text-sm">Start planting to get production tips.</li>
            )}
          </ul>
        </div>
      </section>

      {/* SECTION 3: STRATEGIC GROWTH (Trends & Tech) */}
      <section className="space-y-6 pt-8">
        <div className="flex items-center gap-3 border-b border-slate-200 pb-4">
          <div className="bg-indigo-100 p-2 rounded-lg text-indigo-600">
            <TrendingUp size={24} />
          </div>
          <h2 className="text-2xl font-black text-slate-800 uppercase tracking-tighter">Strategic Growth</h2>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Trajectory Graph */}
          <div className="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 p-8">
            <h3 className="text-xl font-black text-slate-900 mb-2">Your Improvement Over Time</h3>
            <div className="mt-2 mb-4 bg-slate-50 rounded-lg p-3 border border-slate-200">
              <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mb-1">ℹ️ What this tells you</p>
              <p className="text-xs text-slate-600 leading-relaxed">
                Is your success rate going up? Upward trend = You are mastering the climate.
              </p>
            </div>
            {advancedAnalytics?.performance_trends_interpretation && (
              <p className="text-xs font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full inline-block mb-4">
                {advancedAnalytics.performance_trends_interpretation}
              </p>
            )}

            <div className="flex gap-1 mb-4 bg-slate-50 p-1 rounded-xl w-fit">
              {[
                { id: 'weekly', label: 'Weekly' },
                { id: 'monthly', label: 'Monthly' },
                { id: 'quarterly', label: 'Quarterly' },
                { id: 'agrarian', label: 'Agrarian Calendar 🗓️' }
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTimeframe(t.id)}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${timeframe === t.id
                    ? 'bg-white shadow-sm text-indigo-600'
                    : 'text-slate-400 hover:text-slate-600'
                    }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className="h-[250px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={advancedAnalytics?.performance_trends || []}>
                  <defs>
                    <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={true} stroke="#f1f5f9" />
                  <XAxis dataKey="period" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis hide={false} width={30} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#cbd5e1' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="rate" stroke="#6366f1" strokeWidth={3} fill="url(#colorRate)" dot={{ r: 4, fill: '#6366f1' }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Environment & AES Info */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-[2rem] shadow-lg border border-slate-100 flex items-center justify-between">
              <div>
                <div className="text-4xl font-black text-indigo-600">
                  {advancedAnalytics?.advice_effectiveness_score?.aes > 0 ? '+' : ''}{advancedAnalytics?.advice_effectiveness_score?.aes || 0}
                </div>
                <div className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Advice Uplift Score</div>
              </div>
              <div className="text-right max-w-[150px]">
                <p className="text-[10px] text-slate-500 font-medium">
                  Your crops perform better when you follow our advice.
                </p>
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-200">
              <h4 className="font-black text-slate-700 mb-4 flex items-center gap-2">
                <Target size={16} /> Best Weather Conditions
              </h4>
              <div className="flex gap-4">
                {Object.entries(personalInsights?.optimal_conditions || {}).map(([name, data]) => (
                  <div key={name} className="bg-white p-3 rounded-xl border border-slate-100 text-center flex-1">
                    <div className="text-slate-400 uppercase text-[9px] font-black tracking-widest">{name}</div>
                    <div className="text-xl font-black text-slate-800">
                      {data.optimal_value}{name === 'temp' ? '°' : '%'}
                    </div>
                  </div>
                ))}
                {(!personalInsights?.optimal_conditions || Object.keys(personalInsights.optimal_conditions).length === 0) && (
                  <div className="text-xs text-slate-400 italic">Record more data to see optimal weather.</div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Strategy Advice Footer */}
        <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-6">
          <h3 className="text-sm font-black text-indigo-800 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="text-xl">🚀</span> Growth Strategy
          </h3>
          <ul className="space-y-2">
            {advancedAnalytics?.strategic_advice?.strategy?.length > 0 ? (
              advancedAnalytics.strategic_advice.strategy.map((tip, i) => (
                <li key={i} className="text-slate-700 text-sm font-medium flex items-start gap-2">
                  <span className="text-indigo-400 mt-0.5">•</span>
                  <span dangerouslySetInnerHTML={{ __html: tip.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}></span>
                </li>
              ))
            ) : (
              <li className="text-slate-400 italic text-sm">Consistent use unlocks strategic insights.</li>
            )}
          </ul>
        </div>
      </section>

      {/* Financial Modal */}

    </div>
  );
};

export default AnalyticsScreen;