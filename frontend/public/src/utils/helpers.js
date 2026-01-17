/**
 * Helper utility functions
 */

/**
 * Format date to readable string
 */
export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format short date
 */
export const formatShortDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Calculate days until target date
 */
export const daysUntil = (targetDate) => {
  const today = new Date();
  const target = new Date(targetDate);
  const diffTime = target - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

/**
 * Add days to current date
 */
export const addDays = (days) => {
  const result = new Date();
  result.setDate(result.getDate() + days);
  return result.toISOString().split('T')[0];
};

/**
 * Get recommendation style configuration
 */
export const getRecommendationStyle = (action) => {
  const styles = {
    PLANT_NOW: {
      gradient: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800',
      emoji: '✅',
    },
    WAIT: {
      gradient: 'from-yellow-500 to-orange-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      emoji: '⏱️',
    },
    NOT_RECOMMENDED: {
      gradient: 'from-red-500 to-pink-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      emoji: '❌',
    },
  };
  return styles[action] || styles.WAIT;
};

/**
 * Get risk level style
 */
export const getRiskLevelStyle = (riskLevel) => {
  const styles = {
    low: {
      color: 'text-green-800',
      bg: 'bg-green-100',
      border: 'border-green-200',
    },
    medium: {
      color: 'text-yellow-800',
      bg: 'bg-yellow-100',
      border: 'border-yellow-200',
    },
    high: {
      color: 'text-red-800',
      bg: 'bg-red-100',
      border: 'border-red-200',
    },
  };
  return styles[riskLevel] || styles.medium;
};

/**
 * Truncate text
 */
export const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Validate phone number (Tunisian format)
 */
export const validatePhone = (phone) => {
  const phoneRegex = /^216\d{8}$/;
  return phoneRegex.test(phone);
};

/**
 * Validate password strength
 */
export const validatePassword = (password) => {
  if (password.length < 8) return { valid: false, message: 'Password must be at least 8 characters' };
  if (!/[A-Za-z]/.test(password)) return { valid: false, message: 'Password must contain at least one letter' };
  if (!/\d/.test(password)) return { valid: false, message: 'Password must contain at least one number' };
  return { valid: true, message: 'Password is strong' };
};

/**
 * Format currency (Tunisian Dinar)
 */
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return 'N/A';
  return `${amount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} TND`;
};

/**
 * Format weight
 */
export const formatWeight = (kg) => {
  if (kg === null || kg === undefined) return 'N/A';
  return `${kg.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg`;
};

/**
 * Parse error message from API response
 */
export const parseErrorMessage = (error) => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('agridecision_token');
  return !!token;
};

/**
 * Calculate success rate percentage
 */
export const calculateSuccessRate = (successful, total) => {
  if (total === 0) return 0;
  return Math.round((successful / total) * 100);
};