/**
 * Application constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const GOVERNORATES = [
  'Tunis',
  'Ariana',
  'Ben Arous',
  'Manouba',
  'Nabeul',
  'Zaghouan',
  'Bizerte',
  'Beja',
  'Jendouba',
  'Kef',
  'Siliana',
  'Kairouan',
  'Kasserine',
  'Sidi Bouzid',
  'Sousse',
  'Monastir',
  'Mahdia',
  'Sfax',
  'Gabes',
  'Medenine',
  'Tataouine',
  'Gafsa',
  'Tozeur',
  'Kebili',
];

export const FARM_TYPES = {
  RAIN_FED: 'rain_fed',
  IRRIGATED: 'irrigated',
};

export const CROP_ICONS = {
  Wheat: '🌾',
  Tomato: '🍅',
  Potato: '🥔',
  Onion: '🧅',
  Pepper: '🌶️',
  Chickpeas: '🫘',
  Lentils: '🥣',
  Olive: '🫒',
  Citrus: '🍋',
  Almond: '🌰',
  Grape: '🍇',
  'Fava Beans': '🫘',
  Garlic: '🧄',
  'Green Peas': '🫛',
  Okra: '🥘',
  Watermelon: '🍉',
  Carrots: '🥕',
  Zucchini: '🥒',
  'Winter Spinach': '🥬',
  Artichoke: '🌻',
  'Hot Peppers': '🌶️',
};

export const WEATHER_ICONS = {
  Clear: '☀️',
  Clouds: '☁️',
  Rain: '🌧️',
  Drizzle: '🌦️',
  Thunderstorm: '⛈️',
  Snow: '❄️',
  Mist: '🌫️',
  Fog: '🌫️',
};

export const RECOMMENDATION_TYPES = {
  PLANT_NOW: 'PLANT_NOW',
  WAIT: 'WAIT',
  NOT_RECOMMENDED: 'NOT_RECOMMENDED',
};

export const CONFIDENCE_LEVELS = {
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
};

export const OUTCOME_TYPES = {
  SUCCESS: 'success',
  FAILURE: 'failure',
  UNKNOWN: 'unknown',
};

export const LOCAL_STORAGE_KEYS = {
  TOKEN: 'agridecision_token',
  USER: 'agridecision_user',
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Session expired. Please login again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
};

export const SUCCESS_MESSAGES = {
  REGISTRATION: 'Account created successfully!',
  LOGIN: 'Welcome back!',
  ADVICE_RECEIVED: 'Advice generated successfully!',
  OUTCOME_RECORDED: 'Outcome recorded successfully!',
};

// Soil type constants for Tunisia
export const SOIL_TYPES = {
  CLAY: 'CLAY',
  SANDY: 'SANDY',
  LOAM: 'LOAM',
  CALCAREOUS: 'CALCAREOUS',
  SILT: 'SILT',
  UNKNOWN: 'UNKNOWN'
};

export const SOIL_TYPE_OPTIONS = [
  { value: SOIL_TYPES.CLAY, label: 'Clay (Heavy, retains moisture)', emoji: '🟤' },
  { value: SOIL_TYPES.SANDY, label: 'Sandy (Light, drains quickly)', emoji: '🟡' },
  { value: SOIL_TYPES.LOAM, label: 'Loam (Balanced, ideal)', emoji: '🟢' },
  { value: SOIL_TYPES.CALCAREOUS, label: 'Calcareous (High calcium)', emoji: '⚪' },
  { value: SOIL_TYPES.SILT, label: 'Silt (Fine particles)', emoji: '🟠' },
  { value: SOIL_TYPES.UNKNOWN, label: 'Not sure', emoji: '❓' }
];
