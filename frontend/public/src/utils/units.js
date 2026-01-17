/**
 * Unit Conversion Utility
 */

// Constants
const KG_TO_LBS = 2.20462;
const HA_TO_ACRE = 2.47105;
const CELSIUS_TO_FAHRENHEIT_OFFSET = 32;
const CELSIUS_TO_FAHRENHEIT_MULTIPLIER = 9 / 5;

/**
 * Convert weight based on unit system
 * @param {number} value - Value in KG
 * @param {string} system - 'metric' or 'imperial'
 * @returns {number} - Converted value
 */
export const convertWeight = (value, system = 'metric') => {
    if (value === null || value === undefined) return 0;
    if (system === 'imperial') {
        return value * KG_TO_LBS;
    }
    return value; // Default is KG
};

/**
 * Format weight with unit label
 * @param {number} value - Value in KG
 * @param {string} system - 'metric' or 'imperial'
 * @returns {string} - Formatted string (e.g. "10 kg" or "22 lbs")
 */
export const formatWeight = (value, system = 'metric') => {
    const converted = convertWeight(value, system);
    const unit = system === 'imperial' ? 'lbs' : 'kg';
    return `${converted.toFixed(1)} ${unit}`;
};

/**
 * Convert area based on unit system
 * @param {number} value - Value in Hectares
 * @param {string} system - 'metric' or 'imperial'
 * @returns {number} - Converted value
 */
export const convertArea = (value, system = 'metric') => {
    if (value === null || value === undefined) return 0;
    if (system === 'imperial') {
        return value * HA_TO_ACRE;
    }
    return value; // Default is Hectare
};

/**
 * Format area with unit label
 * @param {number} value - Value in Hectares
 * @param {string} system - 'metric' or 'imperial'
 * @returns {string} - Formatted string (e.g. "10 ha" or "24.7 ac")
 */
export const formatArea = (value, system = 'metric') => {
    const converted = convertArea(value, system);
    const unit = system === 'imperial' ? 'ac' : 'ha';
    return `${converted.toFixed(1)} ${unit}`;
};

/**
 * Convert temperature
 * @param {number} value - Value in Celsius
 * @param {string} system - 'metric' or 'imperial'
 * @returns {number} - Converted value
 */
export const convertTemp = (value, system = 'metric') => {
    if (value === null || value === undefined) return 0;
    if (system === 'imperial') {
        return (value * CELSIUS_TO_FAHRENHEIT_MULTIPLIER) + CELSIUS_TO_FAHRENHEIT_OFFSET;
    }
    return value;
};

/**
 * Format temperature with unit label
 * @param {number} value - Value in Celsius
 * @param {string} system - 'metric' or 'imperial'
 * @returns {string} - Formatted string (e.g. "25°C" or "77°F")
 */
export const formatTemp = (value, system = 'metric') => {
    const converted = convertTemp(value, system);
    const unit = system === 'imperial' ? '°F' : '°C';
    return `${converted.toFixed(1)}${unit}`;
};

/**
 * Get display unit label for weight
 */
export const getWeightUnit = (system = 'metric') => system === 'imperial' ? 'lbs' : 'kg';

/**
 * Get display unit label for temperature
 */
export const getTempUnit = (system = 'metric') => system === 'imperial' ? '°F' : '°C';
