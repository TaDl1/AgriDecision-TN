/**
 * Loading spinner component
 */
import React from 'react';
import { Loader } from 'lucide-react';

const LoadingSpinner = ({ size = 'medium', message = 'Loading...', fullScreen = true }) => {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12',
    large: 'w-16 h-16',
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-4 ${fullScreen ? 'min-h-screen w-full fixed inset-0 bg-white/80 z-50' : 'py-8'}`}>
      <Loader className={`${sizeClasses[size]} text-green-600 animate-spin`} />
      {message && <p className="text-gray-600 font-medium animate-pulse">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;