import React, { useState, useEffect, useRef } from 'react';
import {
    Calendar,
    CheckCircle2,
    Clock,
    XCircle,
    AlertTriangle,
    TrendingUp,
    ChevronDown,
    ChevronRight,
    Search
} from 'lucide-react';
import { AGRARIAN_PERIODS, getCurrentPeriod, getPeriodPerformance } from '../utils/agrarianCalendar';
import { CROP_ICONS } from '../utils/constants';

const AgrarianCalendar = ({ user, onCropClick }) => {
    const currentPeriod = getCurrentPeriod();
    const [selectedPeriod, setSelectedPeriod] = useState(currentPeriod);
    const [performance, setPerformance] = useState(getPeriodPerformance(user?.id));

    // Auto-select current on load
    useEffect(() => {
        if (currentPeriod) setSelectedPeriod(currentPeriod);
    }, []);

    const today = new Date().toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    });

    const getStatus = (pId) => {
        const currentIdx = AGRARIAN_PERIODS.findIndex(p => p.id === currentPeriod.id);
        const thisIdx = AGRARIAN_PERIODS.findIndex(p => p.id === pId);
        if (thisIdx === currentIdx) return 'current';
        if (thisIdx < currentIdx) return 'past';
        return 'future';
    };

    return (
        <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden flex flex-col md:flex-row min-h-[600px] animate-fade-in text-slate-900 font-medium">

            {/* LEFT SIDEBAR: STACKED PERIODS (Full Calendar) */}
            <aside className="w-full md:w-72 bg-slate-50/50 border-r border-slate-100 flex flex-col">
                <div className="p-6 border-b border-slate-100 bg-white">
                    <div className="flex items-center gap-2 text-emerald-600 font-black text-xs uppercase tracking-[0.2em] mb-1">
                        <Calendar size={14} />
                        Agricultural Calendar
                    </div>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-none">Full Window Display</p>
                </div>

                <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-hide">
                    {AGRARIAN_PERIODS.map((period) => {
                        const status = getStatus(period.id);
                        const isSelected = selectedPeriod.id === period.id;

                        return (
                            <button
                                key={period.id}
                                onClick={() => setSelectedPeriod(period)}
                                className={`
                                    w-full p-4 rounded-2xl flex items-center justify-between transition-all group
                                    ${isSelected
                                        ? 'bg-white shadow-md border border-slate-100 ring-2 ring-emerald-500/10'
                                        : 'hover:bg-white/50 border border-transparent'}
                                `}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`
                                        w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-black
                                        ${isSelected ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-500'}
                                    `}>
                                        {period.id}
                                    </div>
                                    <div className="text-left">
                                        <h4 className={`text-xs font-black ${isSelected ? 'text-slate-900' : 'text-slate-600'}`}>
                                            {period.name}
                                        </h4>
                                        <p className="text-[9px] font-bold text-slate-400 group-hover:text-emerald-500 transition-colors uppercase tracking-tight">
                                            {period.range}
                                        </p>
                                    </div>
                                </div>
                                {status === 'current' && <CheckCircle2 size={14} className="text-emerald-500 shadow-lg shadow-emerald-200/50" />}
                                {isSelected && <ChevronRight size={14} className="text-slate-300" />}
                            </button>
                        );
                    })}
                </div>

                <div className="p-4 bg-emerald-600 text-white text-center">
                    <p className="text-[10px] font-black uppercase tracking-widest">Today: {today}</p>
                </div>
            </aside>

            {/* RIGHT CONTENT: "OLD INTERFACE" SIDE BY SIDE DETAILS */}
            <main className="flex-1 p-8 flex flex-col overflow-auto scrollbar-hide">
                {/* Header Toggle area for mobile or title */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <span className="px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-xl text-xs font-black ring-1 ring-emerald-200">
                            {getStatus(selectedPeriod.id) === 'current' ? 'CURRENT SEASON' : 'PLANNING MODE'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-10 h-10 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 hover:text-emerald-500 transition-colors cursor-pointer">
                            <Search size={18} />
                        </div>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8 items-start mb-8">
                    {/* Period Detailed Insight */}
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-5xl font-black text-slate-900 tracking-tighter mb-2 leading-[0.9]">
                                {selectedPeriod.name}
                            </h2>
                            <p className="text-emerald-600 font-black text-sm tracking-widest uppercase">
                                Season Window: {selectedPeriod.range}
                            </p>
                        </div>

                        <div className="bg-slate-50/80 rounded-3xl p-6 border border-slate-100">
                            <div className="flex items-center gap-2 text-slate-400 font-black text-[10px] uppercase tracking-widest mb-3">
                                <TrendingUp size={14} />
                                Strategic Insight
                            </div>
                            <p className="text-slate-600 font-bold leading-relaxed italic text-lg pr-4">
                                "{selectedPeriod.description}"
                            </p>
                        </div>

                        <div className="flex items-center gap-1.5 p-4 bg-amber-50 rounded-2xl border border-amber-100">
                            <AlertTriangle size={18} className="text-amber-500 flex-shrink-0" />
                            <p className="text-amber-800 text-[11px] font-black italic">
                                {selectedPeriod.warning}
                            </p>
                        </div>
                    </div>

                    {/* Efficiency Score - Restoring Old Interface feel */}
                    <div className="bg-slate-900 rounded-[2.5rem] p-8 text-white shadow-2xl shadow-slate-200 relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                            <TrendingUp size={120} />
                        </div>

                        <div className="relative z-10 flex flex-col h-full justify-between">
                            <div>
                                <span className="px-3 py-1 bg-white/20 rounded-lg text-[10px] font-black uppercase tracking-widest mb-4 inline-block">Period Efficiency</span>
                                <h3 className="text-6xl font-black text-white leading-none mb-2">
                                    {performance.successRate}%
                                </h3>
                                <p className="text-emerald-400 font-black text-lg uppercase tracking-wider">{performance.rating}</p>
                            </div>

                            <div className="mt-12 pt-8 border-t border-white/10">
                                <p className="text-xs text-slate-400 font-bold leading-relaxed mb-4">
                                    Historical analysis shows this window provides optimal conditions for tuber development and leaf vigor.
                                </p>
                                <button
                                    onClick={() => onCropClick && onCropClick(selectedPeriod.suitable[0])}
                                    className="w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-white rounded-2xl font-black uppercase tracking-widest transition-all shadow-lg shadow-emerald-900/40"
                                >
                                    Optimize Season 🚀
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Suitability Matrix */}
                <div className="grid md:grid-cols-3 gap-6 mt-auto">
                    <div className="bg-emerald-50/50 p-6 rounded-3xl border border-emerald-100">
                        <div className="flex items-center gap-2 text-emerald-800 font-black text-[10px] uppercase tracking-[0.2em] mb-4">
                            <CheckCircle2 size={16} className="text-emerald-600" />
                            Suitable
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {selectedPeriod.suitable.map((c) => (
                                <button
                                    key={c}
                                    onClick={() => onCropClick && onCropClick(c)}
                                    className="px-4 py-2 bg-white rounded-xl border border-emerald-100 shadow-sm text-xs font-black text-emerald-900 hover:scale-105 transition-transform flex items-center gap-2"
                                >
                                    <span>{CROP_ICONS[c] || '🌱'}</span>
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="bg-blue-50/50 p-6 rounded-3xl border border-blue-100">
                        <div className="flex items-center gap-2 text-blue-800 font-black text-[10px] uppercase tracking-[0.2em] mb-4">
                            <Clock size={16} className="text-blue-600" />
                            Wait / Prepare
                        </div>
                        <div className="space-y-3">
                            {selectedPeriod.wait.map((item) => (
                                <div key={item.name} className="bg-white p-3 rounded-xl border border-blue-50">
                                    <p className="font-black text-slate-800 text-[11px] flex items-center gap-2">
                                        <span>{CROP_ICONS[item.name] || '⏳'}</span>
                                        {item.name}
                                    </p>
                                    <p className="text-[9px] text-slate-400 font-bold uppercase tracking-tight mt-1">{item.reason}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-red-50/50 p-6 rounded-3xl border border-red-100">
                        <div className="flex items-center gap-2 text-red-800 font-black text-[10px] uppercase tracking-[0.2em] mb-4">
                            <XCircle size={16} className="text-red-600" />
                            Not Recommended
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {selectedPeriod.avoid.map((c) => (
                                <span key={c} className="px-3 py-1.5 bg-white/70 rounded-lg text-[10px] font-bold text-slate-400 border border-red-50">
                                    {c}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default AgrarianCalendar;
