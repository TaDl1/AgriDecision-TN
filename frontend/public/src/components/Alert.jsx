/**
 * Alert notification component
 */
import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

const Alert = ({ type = 'info', message, onClose, autoClose = false, duration = 5000 }) => {
  React.useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, onClose]);

  const config = {
    success: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800',
      icon: <CheckCircle size={24} />,
    },
    error: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      icon: <XCircle size={24} />,
    },
    warning: {
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      icon: <AlertTriangle size={24} />,
    },
    info: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      icon: <Info size={24} />,
    },
  };

  const style = config[type] || config.info;

  return (
    <div
      className={`
        ${style.bgColor} ${style.borderColor} ${style.textColor}
        border-2 rounded-xl p-4 flex items-start gap-3 animate-slide-up
      `}
    >
      <div className="flex-shrink-0">{style.icon}</div>
      <div className="flex-1">{message}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 hover:opacity-70 transition-opacity"
          aria-label="Close alert"
        >
          <X size={20} />
        </button>
      )}
    </div>
  );
};

export default Alert;