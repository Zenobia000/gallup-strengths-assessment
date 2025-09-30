/**
 * API Service - Gallup Strengths Assessment
 * Handles all HTTP communication with FastAPI backend
 * Version: 1.0
 */

import { config } from './config.js';

class API {
  constructor() {
    this.baseURL = config.getApiBaseURL();
    this.timeout = config.getApiConfig().timeout;
    this.retries = config.getApiConfig().retries;
    this.headers = {
      'Content-Type': 'application/json',
    };

    // Log configuration in development
    config.logInfo();
  }

  /**
   * Generic HTTP request handler with retry logic
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
      signal: AbortSignal.timeout(this.timeout),
      ...options,
    };

    // Add body for non-GET requests
    if (data && method !== 'GET') {
      config.body = JSON.stringify(data);
    }

    let lastError;

    // Retry logic
    for (let attempt = 1; attempt <= this.retries; attempt++) {
      try {
        if (config.isFeatureEnabled && config.isFeatureEnabled('debug')) {
          console.log(`🌐 API Request (attempt ${attempt}/${this.retries}):`, method, endpoint);
        }

        const response = await fetch(url, config);

        // Handle non-OK responses
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const apiError = new APIError(
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
          );

          // Don't retry client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            throw apiError;
          }

          lastError = apiError;
          continue; // Retry for 5xx errors
        }

        // Return parsed JSON
        const result = await response.json();

        if (config.isFeatureEnabled && config.isFeatureEnabled('debug')) {
          console.log('✅ API Response:', result);
        }

        return result;
      } catch (error) {
        lastError = error;

        // Don't retry API errors with client status codes
        if (error instanceof APIError && error.statusCode >= 400 && error.statusCode < 500) {
          throw error;
        }

        // Don't retry on the last attempt
        if (attempt === this.retries) {
          break;
        }

        // Wait before retry (exponential backoff)
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    // All retries failed
    if (lastError instanceof APIError) {
      throw lastError;
    }

    throw new APIError(
      lastError?.message || 'Network error occurred',
      0,
      { originalError: lastError }
    );
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
   * Get all assessment questions with situational support
   * @param {boolean} includeSituational - Include situational questions
   * @returns {Promise<Object>} Questions data
   */
  async getQuestions(includeSituational = true) {
    const params = includeSituational ? '?include_situational=true' : '';
    return this.get(`/questions${params}`);
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
    // Transform answers to match API schema
    const responses = answers.map(answer => ({
      item_id: String(answer.question_id),
      response: answer.score
    }));

    // Calculate completion time (assume 5 seconds per question minimum)
    const completion_time = Math.max(answers.length * 5, 60);

    return this.post(`/sessions/${sessionId}/submit`, {
      responses,
      completion_time
    });
  }

  // ============================================
  // Scoring API
  // ============================================

  /**
   * Submit responses for scoring
   * @param {Object} scoringData - Scoring request data
   * @returns {Promise<Object>} Scoring results
   */
  async submitForScoring(scoringData) {
    return this.post('/scoring/calculate', scoringData);
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
    // First, try to get results from localStorage (most recent session)
    try {
      const storedResults = localStorage.getItem('assessment_results');
      if (storedResults) {
        const parsedResults = JSON.parse(storedResults);

        // Check if the stored results match the requested session and are recent (within 1 hour)
        const isRecent = Date.now() - parsedResults.timestamp < 60 * 60 * 1000;
        const isMatchingSession = !sessionId || parsedResults.session_id === sessionId;

        if (isRecent && isMatchingSession && parsedResults.scores) {
          return {
            success: true,
            data: {
              session_id: parsedResults.session_id,
              scores: parsedResults.scores,
              strengths: this._computeBasicStrengths(parsedResults.scores),
              message: "基於您最近的評估結果",
              source: "localStorage"
            }
          };
        }
      }
    } catch (localStorageError) {
      console.warn('Failed to parse localStorage results:', localStorageError);
    }

    // Try to get results from the results API endpoint
    try {
      return await this.get(`/results/${sessionId}`);
    } catch (error) {
      // If results endpoint fails, try to get raw scores and construct basic results
      console.warn('Results endpoint failed, trying to construct from raw scores:', error);

      try {
        // Check if we can get the scores from the database via a different endpoint
        const scoringData = await this.get(`/scores/${sessionId}`);

        if (scoringData && scoringData.raw_scores) {
          return {
            success: true,
            data: {
              session_id: sessionId,
              scores: scoringData.raw_scores,
              strengths: this._computeBasicStrengths(scoringData.raw_scores),
              message: "基於您的評估分數生成的基本優勢分析",
              source: "database"
            }
          };
        }

        throw new Error('No scoring data available');
      } catch (secondError) {
        console.error('Failed to get any results data:', secondError);

        // Return a basic error message instead of hardcoded mock data
        return {
          success: false,
          error: {
            message: "無法載入評估結果，請稍後再試或重新進行評估",
            code: "RESULTS_NOT_AVAILABLE"
          }
        };
      }
    }
  }

  /**
   * Compute basic strengths from Big Five scores
   * @param {Object} scores - Big Five scores
   * @returns {Array} Basic strengths list
   */
  _computeBasicStrengths(scores) {
    const strengthsMapping = {
      openness: { name: "創新思維", baseScore: 70 },
      conscientiousness: { name: "執行力", baseScore: 65 },
      extraversion: { name: "影響力", baseScore: 60 },
      agreeableness: { name: "協作精神", baseScore: 55 },
      neuroticism: { name: "壓力管理", baseScore: 50, reverse: true }
    };

    const strengthsList = [];

    Object.entries(scores).forEach(([dimension, score]) => {
      const mapping = strengthsMapping[dimension];
      if (mapping) {
        let adjustedScore = mapping.baseScore;

        // Adjust score based on dimension score (normalized from raw score)
        const normalizedScore = Math.max(0, Math.min(100, (score / 20) * 100));

        if (mapping.reverse) {
          // For neuroticism, higher score means better stress management
          adjustedScore = mapping.baseScore + (100 - normalizedScore) * 0.3;
        } else {
          adjustedScore = mapping.baseScore + normalizedScore * 0.3;
        }

        strengthsList.push({
          name: mapping.name,
          score: Math.round(adjustedScore * 100) / 100,
          description: `基於您在${dimension}向度的表現計算得出`,
          dimension: dimension
        });
      }
    });

    // Sort by score descending
    return strengthsList.sort((a, b) => b.score - a.score);
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