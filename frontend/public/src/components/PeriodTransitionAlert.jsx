import React from 'react';
import { AlertCircle, ArrowRight, Thermometer, Droplets, Info } from 'lucide-react';

const PeriodTransitionAlert = ({ currentPeriod, nextPeriod, daysRemaining }) => {
    // Only show if we have valid data and transition is soon (e.g. within 14 days)
    if (!currentPeriod || !nextPeriod || daysRemaining > 14) return null;

    return (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-6 shadow-sm relative overflow-hidden animate-fade-in">
            <div className="absolute top-0 right-0 p-4 opacity-10 text-amber-500">
                <AlertCircle size={100} />
            </div>

            <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                    <div className="bg-amber-100 p-2 rounded-full text-amber-600 animate-pulse">
                        <AlertCircle size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-amber-900">
                        Period Change in {daysRemaining} Days
                    </h3>
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-white/60 rounded-full text-xs font-bold text-amber-800 border border-amber-100 ml-auto">
                        <span className="uppercase">{currentPeriod.id}</span>
                        <ArrowRight size={12} />
                        <span className="uppercase">{nextPeriod.id}</span>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                    <div className="flex-1">
                        <p className="text-amber-800 font-medium mb-3">
                            Transitioning from <strong>{currentPeriod.name}</strong> to <strong>{nextPeriod.name}</strong>
                        </p>

                        <div className="bg-white/60 rounded-xl p-4 border border-amber-100/50">
                            <h4 className="text-xs font-bold uppercase text-amber-600 mb-2 tracking-wide">Prepare For:</h4>
                            <ul className="space-y-2">
                                {nextPeriod.characteristics.map((char, index) => (
                                    <li key={index} className="flex items-start gap-2 text-sm text-slate-700">
                                        <div className="mt-0.5 text-amber-500">•</div>
                                        <span>{char}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="md:w-1/3 flex flex-col justify-between">
                        <div>
                            <h4 className="text-xs font-bold uppercase text-amber-600 mb-2 tracking-wide">Recommended Actions:</h4>
                            <div className="space-y-2 text-sm text-amber-900/80">
                                <div className="flex items-center gap-2">
                                    <Thermometer size={16} className="text-orange-500" />
                                    <span>Check heat tolerance</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Droplets size={16} className="text-blue-500" />
                                    <span>Adjust irrigation plan</span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-4 pt-3 border-t border-amber-200/50">
                            <p className="text-xs text-amber-800">
                                <strong>Next Best Crops:</strong> {nextPeriod.bestCrops.slice(0, 2).join(', ')}...
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PeriodTransitionAlert;
