/**
 * API service for backend communication
 */
import { API_BASE_URL, LOCAL_STORAGE_KEYS } from '../utils/constants';

class APIService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get authentication token from localStorage
   */
  getToken() {
    return localStorage.getItem(LOCAL_STORAGE_KEYS.TOKEN);
  }

  /**
   * Set authentication token in localStorage
   */
  setToken(token) {
    localStorage.setItem(LOCAL_STORAGE_KEYS.TOKEN, token);
  }

  /**
   * Remove authentication token
   */
  removeToken() {
    localStorage.removeItem(LOCAL_STORAGE_KEYS.TOKEN);
  }

  /**
   * Get default headers
   */
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log('✅ Authorization header set with token');
      } else {
        console.warn('⚠️ No token found in localStorage');
      }
    }

    return headers;
  }

  /**
   * Generic request handler
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: this.getHeaders(options.requireAuth !== false),
    };

    try {
      console.log(`📡 Sending ${config.method || 'GET'} to ${url}`);
      console.log(`📦 Request body:`, config.body);
      console.log(`📋 Headers:`, config.headers);

      const response = await fetch(url, config);
      const data = await response.json();

      console.log(`📨 Response status: ${response.status}`);
      console.log(`📨 Response data:`, data);

      if (!response.ok) {
        // Extract error message from different response formats
        let errorMessage = 'Request failed';

        if (data.payload?.errors) {
          // Validation error with detailed messages
          const errors = data.payload.errors;
          errorMessage = typeof errors === 'object'
            ? Object.entries(errors).map(([key, val]) => `${key}: ${Array.isArray(val) ? val[0] : val}`).join(', ')
            : String(errors);
        } else if (data.error) {
          errorMessage = data.error;
        } else if (data.message) {
          errorMessage = data.message;
        }

        console.error(`❌ API Error [${response.status}]:`, {
          endpoint,
          status: response.status,
          error: errorMessage,
          details: data.details,
          fullResponse: data
        });

        if (data.details) {
          errorMessage += `: ${data.details}`;
        }

        throw new Error(errorMessage);
      }

      // Automatically unwrap data payload if it exists
      return data.data !== undefined ? data.data : data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ========== AUTH ENDPOINTS ==========

  async register(userData) {
    // Ensure phone number has 216 prefix
    const processedData = {
      ...userData,
      phone_number: userData.phone_number.startsWith('216')
        ? userData.phone_number
        : '216' + userData.phone_number
    };

    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(processedData),
      requireAuth: false,
    });
  }

  async login(phone, password) {
    // Ensure phone number has 216 prefix
    const processedPhone = phone.startsWith('216')
      ? phone
      : '216' + phone;

    const response = await this.request(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ phone: processedPhone, password }),
        requireAuth: false,
      }
    );

    if (response.token) {
      this.setToken(response.token);
    }

    return response;
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  async logout() {
    this.removeToken();
    localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
  }

  // ========== CROP ENDPOINTS ==========

  async getCrops() {
    return this.request('/crops/', { requireAuth: false });
  }

  async getCropDetails(cropId) {
    return this.request(`/crops/${cropId}`, { requireAuth: false });
  }

  async getAgrarianPeriods() {
    return this.request('/crops/periods', { requireAuth: false });
  }

  // ========== DECISION ENDPOINTS ==========

  async getAdvice(cropId, governorate = null, seedlingCost = null, marketPrice = null, inputQuantity = null) {
    // Ensure cropId is an integer
    const parsedId = parseInt(cropId, 10);
    console.log('🎯 Getting advice for crop:', {
      original_cropId: cropId,
      original_type: typeof cropId,
      parsed_id: parsedId,
      parsed_type: typeof parsedId,
      is_valid_number: !isNaN(parsedId),
      governorate,
      seedlingCost,
      marketPrice,
      inputQuantity,
    });

    if (isNaN(parsedId)) {
      console.error('❌ Invalid crop ID - not a number:', cropId);
      throw new Error(`Invalid crop ID: ${cropId}`);
    }

    const body = { crop_id: parsedId };
    if (governorate) {
      body.governorate = governorate;
    }
    if (seedlingCost !== null && seedlingCost !== undefined) {
      body.seedling_cost = parseFloat(seedlingCost);
    }
    if (marketPrice !== null && marketPrice !== undefined) {
      body.market_price = parseFloat(marketPrice);
    }
    if (inputQuantity !== null && inputQuantity !== undefined) {
      body.input_quantity = parseFloat(inputQuantity);
    }

    console.log('📤 Sending request body:', JSON.stringify(body), 'Types:', {
      crop_id: typeof body.crop_id,
      seedling_cost: typeof body.seedling_cost,
      market_price: typeof body.market_price,
      input_quantity: typeof body.input_quantity
    });

    return this.request('/decisions/get-advice', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /**
   * Get decision history
   */
  async getDecisionHistory(limit = 20, offset = 0, filters = {}) {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    for (const key in filters) {
      if (Object.prototype.hasOwnProperty.call(filters, key) && filters[key] !== undefined && filters[key] !== null) {
        params.append(key, filters[key].toString());
      }
    }
    return this.request(`/decisions/history?${params.toString()}`);
  }

  /**
   * Get metadata for history filters
   */
  async getHistoryFilters() {
    return this.request('/decisions/history/filters');
  }

  async recordOutcome(decisionId, outcomeData) {
    return this.request('/decisions/record-outcome', {
      method: 'POST',
      body: JSON.stringify({
        decision_id: decisionId,
        ...outcomeData,
      }),
    });
  }

  async getDecisionDetails(decisionId) {
    return this.request(`/decisions/${decisionId}`);
  }

  async getDecisionStats() {
    return this.request('/decisions/stats');
  }

  // ========== ANALYTICS ENDPOINTS ==========

  async getPersonalAnalytics() {
    return this.request('/decisions/stats'); // Kept original as stats
  }

  /**
   * Get regional benchmark (GSI, PBD, RCPS, RRAP)
   */
  async getRegionalBenchmark() {
    return this.request('/analytics/regional-benchmark');
  }

  /**
   * Get personal insights (best crop, period, temp)
   */
  async getPersonalInsights() {
    return this.request('/analytics/personal-insights');
  }

  /**
   * Record farmer's action after receiving advice
   */
  async recordAction(decisionId, actualAction, deviationReason = null) {
    return this.request(`/decisions/${decisionId}/record-action`, {
      method: 'POST',
      body: JSON.stringify({
        actual_action: actualAction,
        deviation_reason: deviationReason
      }),
    });
  }

  /**
   * Get advanced analytics (AES, FCI, RAR, CVS, TLS, CSAA)
   */
  async getAdvancedAnalytics(timeframe = 'monthly') {
    return this.request(`/decisions/advanced-analytics?timeframe=${timeframe}`);
  }

  /**
   * Get smart natural language summary of analytics
   */
  async getSmartSummary() {
    return this.request('/analytics/smart-summary');
  }

  async simulateData() {
    return this.request('/decisions/simulate-data', {
      method: 'POST'
    });
  }

  async parseVoice(text) {
    return this.request('/voice/parse', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  }

  // ========== UPDATE & DELETE OPERATIONS ==========

  async updateProfile(userData) {
    return this.request('/auth/update-profile', {
      method: 'PUT',
      body: JSON.stringify(userData)
    });
  }

  async updatePreferences(preferences) {
    return this.request('/auth/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences)
    });
  }

  async deleteAccount() {
    return this.request('/auth/account', {
      method: 'DELETE'
    });
  }

  async updateDecisionOutcome(decisionId, outcomeData) {
    return this.request(`/decisions/${decisionId}/outcome`, {
      method: 'PUT',
      body: JSON.stringify(outcomeData)
    });
  }

  async updateAdviceAction(decisionId, actionData) {
    return this.request(`/decisions/${decisionId}/action`, {
      method: 'PUT',
      body: JSON.stringify(actionData)
    });
  }

  async deleteDecision(decisionId) {
    return this.request(`/decisions/${decisionId}`, {
      method: 'DELETE'
    });
  }

  // ========== HEALTH CHECK ==========

  async healthCheck() {
    return this.request('/health', { requireAuth: false });
  }
}

export default new APIService();