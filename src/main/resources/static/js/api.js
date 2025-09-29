/**
 * API Service - Gallup Strengths Assessment
 * Handles all HTTP communication with FastAPI backend
 * Version: 1.0
 */

class API {
  constructor() {
    this.baseURL = 'http://localhost:8002/api/v1';
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Generic HTTP request handler
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
   * @param {string} endpoint - API endpoint path
   * @param {Object|null} data - Request body data
   * @param {Object} options - Additional fetch options
   * @returns {Promise<Object>} Response data
   */
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      method,
      headers: { ...this.headers, ...options.headers },
      ...options,
    };

    // Add body for non-GET requests
    if (data && method !== 'GET') {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, config);

      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      // Return parsed JSON
      return await response.json();
    } catch (error) {
      // Re-throw API errors
      if (error instanceof APIError) {
        throw error;
      }

      // Network or other errors
      throw new APIError(
        error.message || 'Network error occurred',
        0,
        { originalError: error }
      );
    }
  }

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>}
   */
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, null, options);
  }

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>}
   */
  async post(endpoint, data, options = {}) {
    return this.request('POST', endpoint, data, options);
  }

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>}
   */
  async put(endpoint, data, options = {}) {
    return this.request('PUT', endpoint, data, options);
  }

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>}
   */
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, null, options);
  }

  // ============================================
  // Consent API
  // ============================================

  /**
   * Submit user consent
   * @param {Object} consentData - Consent information
   * @returns {Promise<Object>} Session data with session_id
   */
  async submitConsent(consentData) {
    return this.post('/consent', consentData);
  }

  // ============================================
  // Session API
  // ============================================

  /**
   * Create new assessment session
   * @returns {Promise<Object>} Session data
   */
  async createSession() {
    return this.post('/sessions');
  }

  /**
   * Get session details
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Session data
   */
  async getSession(sessionId) {
    return this.get(`/sessions/${sessionId}`);
  }

  // ============================================
  // Questions API
  // ============================================

  /**
   * Get all assessment questions
   * @returns {Promise<Object>} Questions data
   */
  async getQuestions() {
    return this.get('/questions');
  }

  /**
   * Submit answer for a question
   * @param {string} sessionId - Session ID
   * @param {Object} answerData - Answer data
   * @returns {Promise<Object>} Submission result
   */
  async submitAnswer(sessionId, answerData) {
    return this.post(`/sessions/${sessionId}/answers`, answerData);
  }

  /**
   * Submit all answers at once
   * @param {string} sessionId - Session ID
   * @param {Array} answers - Array of answers
   * @returns {Promise<Object>} Submission result
   */
  async submitAllAnswers(sessionId, answers) {
    return this.post(`/sessions/${sessionId}/submit`, { answers });
  }

  // ============================================
  // Results API
  // ============================================

  /**
   * Get assessment results
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Results data with strengths
   */
  async getResults(sessionId) {
    return this.get(`/sessions/${sessionId}/results`);
  }

  /**
   * Get recommendations based on results
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Recommendations data
   */
  async getRecommendations(sessionId) {
    return this.get(`/sessions/${sessionId}/recommendations`);
  }

  // ============================================
  // Report API
  // ============================================

  /**
   * Generate PDF report
   * @param {string} sessionId - Session ID
   * @returns {Promise<Blob>} PDF file blob
   */
  async generateReport(sessionId) {
    const response = await fetch(
      `${this.baseURL}/sessions/${sessionId}/report`,
      {
        method: 'GET',
        headers: this.headers,
      }
    );

    if (!response.ok) {
      throw new APIError(
        'Failed to generate report',
        response.status
      );
    }

    return await response.blob();
  }

  /**
   * Get shareable report link
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Share link data
   */
  async getShareLink(sessionId) {
    return this.get(`/sessions/${sessionId}/share`);
  }

  // ============================================
  // Health Check
  // ============================================

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    return this.get('/health');
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, statusCode, data = {}) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.data = data;
  }
}

// Export singleton instance
const api = new API();
export { api, APIError };