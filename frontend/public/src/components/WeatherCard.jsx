import React from 'react';
import { Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, Snowflake } from 'lucide-react';
import { formatTemp } from '../utils/units';

const WeatherCard = ({ forecast, units = 'metric', lang = 'en-US' }) => {
  const getIcon = (condition) => {
    const c = condition?.toLowerCase() || '';
    if (c.includes('rain') || c.includes('drizzle')) return <CloudRain className="text-blue-500 drop-shadow-lg" size={32} />;
    if (c.includes('cloud')) return <Cloud className="text-slate-400 drop-shadow-md" size={32} />;
    if (c.includes('wind')) return <Wind className="text-teal-500 drop-shadow-md" size={32} />;
    if (c.includes('cold') || c.includes('snow')) return <Snowflake className="text-cyan-400 drop-shadow-lg" size={32} />;
    return <Sun className="text-orange-400 drop-shadow-lg animate-pulse-slow" size={32} />;
  };

  const getGradient = (condition) => {
    const c = condition?.toLowerCase() || '';
    if (c.includes('rain')) return 'from-blue-50 to-slate-100 border-blue-200';
    if (c.includes('sunny') || c.includes('clear')) return 'from-orange-50 to-amber-50 border-orange-200';
    if (c.includes('cloud')) return 'from-slate-50 to-gray-100 border-slate-200';
    return 'from-white to-slate-50 border-slate-100';
  };

  return (
    <div className={`
      relative overflow-hidden rounded-2xl p-4 flex flex-col items-center text-center
      bg-gradient-to-b ${getGradient(forecast.condition)}
      border transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group
    `}>
      {/* Date */}
      <span className="text-[10px] font-black tracking-widest text-slate-400 uppercase mb-3">
        {new Date(forecast.date).toLocaleDateString(lang, { weekday: 'short', day: 'numeric' })}
      </span>

      {/* Icon */}
      <div className="mb-3 transform group-hover:scale-110 transition-transform duration-300">
        {getIcon(forecast.condition)}
      </div>

      {/* Temps */}
      <div className="flex items-baseline gap-1 mb-2">
        <span className="text-2xl font-black text-slate-800">
          {formatTemp(forecast.temp_max, units).replace(/[A-Za-z°]/g, '')}°
        </span>
        <span className="text-xs font-bold text-slate-400">
          / {formatTemp(forecast.temp_min, units)}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="flex gap-2 mt-auto pt-2 border-t border-black/5 w-full justify-center">
        {forecast.rainfall > 0 && (
          <div className="flex items-center gap-1 text-[10px] font-bold text-blue-600 bg-blue-100/50 px-1.5 py-0.5 rounded-md">
            <Droplets size={10} />
            {forecast.rainfall}mm
          </div>
        )}
        {forecast.humidity && (
          <div className="flex items-center gap-1 text-[10px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded-md">
            <Thermometer size={10} />
            {Math.round(forecast.humidity)}%
          </div>
        )}
      </div>

      {/* Condition Text */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <span className="text-[9px] font-bold bg-white/80 backdrop-blur px-2 py-1 rounded-lg text-slate-600 shadow-sm">
          {forecast.condition}
        </span>
      </div>
    </div>
  );
};

export default WeatherCard;