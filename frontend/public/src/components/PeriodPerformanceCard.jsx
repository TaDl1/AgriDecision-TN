import React from 'react';
import { Calendar, TrendingUp, AlertTriangle, CheckCircle2, XCircle, Clock } from 'lucide-react';

const PeriodPerformanceCard = ({ period, performance }) => {
    if (!period) return null;

    return (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 relative overflow-hidden h-full">
            {/* Background Decorative Elements */}
            <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                <Calendar size={120} />
            </div>

            <div className="relative z-10 h-full flex flex-col">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-4">

                    {/* Header Section */}
                    <div className="flex-1">
                        <h3 className="text-slate-500 text-sm font-bold uppercase tracking-wide mb-1">
                            Agricultural Calendar
                        </h3>
                        <div className="flex flex-wrap items-baseline gap-2 mb-2">
                            <h2 className="text-2xl font-bold text-slate-800">
                                {period.name}
                            </h2>
                            <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-bold text-slate-500 border border-slate-200 uppercase tracking-tighter">
                                {period.id}
                            </span>
                        </div>
                        <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-sm font-medium border border-emerald-100 mb-2">
                            <Calendar size={14} />
                            {period.range}
                        </div>

                        {/* Warning Banner */}
                        <div className="flex items-start gap-2 bg-amber-50 p-2 rounded-lg border border-amber-100 text-amber-800 text-xs mt-2 max-w-md">
                            <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                            <p>{period.warning}</p>
                        </div>
                    </div>

                    {/* Performance Badge */}
                    <div className="md:border-l md:border-slate-100 md:pl-6 flex flex-col justify-center min-w-[140px] text-right md:text-left">
                        <span className="text-slate-500 text-xs font-bold block mb-1">Efficiency Score</span>
                        <div className="text-4xl font-bold text-emerald-600 tracking-tight">
                            {performance.successRate}%
                        </div>
                        <div className="text-emerald-600 text-xs font-bold uppercase tracking-wide">
                            {performance.rating}
                        </div>
                    </div>
                </div>

                <hr className="border-slate-100 mb-4" />

                {/* Crops Categories */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
                    {/* Recommended */}
                    <div className="bg-emerald-50/50 rounded-xl p-3 border border-emerald-100">
                        <div className="flex items-center gap-2 mb-2 text-emerald-800 font-bold text-sm uppercase tracking-wide">
                            <CheckCircle2 size={16} className="text-emerald-500" />
                            Suitable
                        </div>
                        <ul className="space-y-1.5">
                            {period.recommended && period.recommended.map((crop) => (
                                <li key={crop} className="text-sm text-slate-700 flex items-start gap-2">
                                    <span className="block w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></span>
                                    <span className="leading-tight">{crop}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Wait */}
                    <div className="bg-blue-50/50 rounded-xl p-3 border border-blue-100">
                        <div className="flex items-center gap-2 mb-2 text-blue-800 font-bold text-sm uppercase tracking-wide">
                            <Clock size={16} className="text-blue-500" />
                            Wait / Prepare
                        </div>
                        <ul className="space-y-1.5">
                            {period.wait && period.wait.map((crop) => (
                                <li key={crop} className="text-sm text-slate-700 flex items-start gap-2">
                                    <span className="block w-1.5 h-1.5 rounded-full bg-blue-300 mt-1.5 shrink-0"></span>
                                    <span className="leading-tight">{crop}</span>
                                </li>
                            ))}
                            {(!period.wait || period.wait.length === 0) && (
                                <li className="text-xs text-slate-400 italic">No specific crops to wait for in this period.</li>
                            )}
                        </ul>
                    </div>

                    {/* Avoid */}
                    <div className="bg-red-50/50 rounded-xl p-3 border border-red-100">
                        <div className="flex items-center gap-2 mb-2 text-red-800 font-bold text-sm uppercase tracking-wide">
                            <XCircle size={16} className="text-red-500" />
                            Not Recommended
                        </div>
                        <ul className="space-y-1.5">
                            {period.avoid && period.avoid.map((crop) => (
                                <li key={crop} className="text-sm text-slate-700 flex items-start gap-2">
                                    <span className="block w-1.5 h-1.5 rounded-full bg-red-300 mt-1.5 shrink-0"></span>
                                    <span className="leading-tight">{crop}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default PeriodPerformanceCard;
