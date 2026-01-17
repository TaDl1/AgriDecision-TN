/**
 * Form validation utilities
 */

export const validateRegistrationForm = (data) => {
  const errors = {};

  // Phone validation - accept with or without 216 prefix
  if (!data.phone_number) {
    errors.phone_number = 'Phone number is required';
  } else {
    // Remove 216 prefix if present for validation
    const phoneWithoutPrefix = data.phone_number.startsWith('216')
      ? data.phone_number
      : '216' + data.phone_number;

    if (!/^216\d{8}$/.test(phoneWithoutPrefix)) {
      errors.phone_number = 'Phone must be 8 digits (e.g., 12345678)';
    }
  }

  // Name validation
  if (!data.first_name) {
    errors.first_name = 'First name is required';
  }

  if (!data.last_name) {
    errors.last_name = 'Last name is required';
  }

  // Password validation
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  } else if (!/[A-Za-z]/.test(data.password)) {
    errors.password = 'Password must contain at least one letter';
  } else if (!/\d/.test(data.password)) {
    errors.password = 'Password must contain at least one number';
  }

  // Governorate validation
  if (!data.governorate) {
    errors.governorate = 'Governorate is required';
  }

  // Farm type validation
  if (!data.farm_type) {
    errors.farm_type = 'Farm type is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateLoginForm = (data) => {
  const errors = {};

  if (!data.phone) {
    errors.phone = 'Phone number is required';
  } else {
    // Remove 216 prefix if present for validation
    const phoneWithoutPrefix = data.phone.startsWith('216')
      ? data.phone
      : '216' + data.phone;

    if (!/^216\d{8}$/.test(phoneWithoutPrefix)) {
      errors.phone = 'Phone must be 8 digits (e.g., 12345678)';
    }
  }

  if (!data.password) {
    errors.password = 'Password is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateOutcomeForm = (data) => {
  const errors = {};

  if (!data.outcome) {
    errors.outcome = 'Outcome is required';
  }

  if (data.yield_kg !== undefined && data.yield_kg < 0) {
    errors.yield_kg = 'Yield must be positive';
  }

  if (data.revenue_tnd !== undefined && data.revenue_tnd < 0) {
    errors.revenue_tnd = 'Revenue must be positive';
  }

  if (data.notes && data.notes.length > 500) {
    errors.notes = 'Notes must be less than 500 characters';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};