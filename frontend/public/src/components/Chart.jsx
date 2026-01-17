/**
 * Simple chart component for analytics
 */
import React from 'react';

const Chart = ({ data, type = 'bar', height = 200 }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-xl">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <div className="h-full flex items-end justify-around gap-2">
        {data.map((item, index) => (
          <div key={index} className="flex-1 flex flex-col items-center">
            <div
              className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-lg transition-all hover:from-blue-700 hover:to-blue-500 cursor-pointer relative group"
              style={{ height: `${(item.value / maxValue) * 100}%` }}
              title={`${item.label}: ${item.value}`}
            >
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-white text-xs px-2 py-1 rounded">
                {item.value}
              </div>
            </div>
            <div className="text-xs mt-2 font-semibold text-gray-600 text-center">
              {item.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Chart;