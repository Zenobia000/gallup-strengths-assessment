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
  // Results API
  // ============================================

  /**
   * Get assessment results
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Results data with strengths
   */
  async getResults(sessionId) {
    // For MVP, return properly formatted mock data that matches what results.html expects
    // This will be replaced with actual API endpoint later
    return {
      success: true,
      data: {
        session_id: sessionId,
        scores: {
          openness: 85,
          conscientiousness: 78,
          extraversion: 72,
          agreeableness: 80,
          neuroticism: 45
        },
        strengths: [
          {
            name: "Strategic",
            score: 92.5,
            description: "您擅長制定長遠計劃，能夠看到大局並預見潛在的挑戰和機會。"
          },
          {
            name: "Learner",
            score: 88.3,
            description: "您熱愛學習新知識，不斷追求自我提升和成長。"
          },
          {
            name: "Analytical",
            score: 85.7,
            description: "您善於分析複雜問題，用邏輯和數據支持決策。"
          },
          {
            name: "Achiever",
            score: 82.1,
            description: "您有強烈的成就動機，每天都需要完成一些事情來感到滿足。"
          },
          {
            name: "Responsibility",
            score: 79.4,
            description: "您對承諾非常認真，值得信賴，總是信守諾言。"
          },
          {
            name: "Input",
            score: 76.8,
            description: "您喜歡收集和歸檔各種資訊，是一個知識的收藏家。"
          },
          {
            name: "Intellection",
            score: 74.2,
            description: "您喜歡思考，享受獨處和深度思考的時光。"
          },
          {
            name: "Focus",
            score: 71.5,
            description: "您能夠確定優先順序，保持專注，朝著目標前進。"
          },
          {
            name: "Deliberative",
            score: 68.9,
            description: "您做決定時謹慎小心，仔細考慮所有選項。"
          },
          {
            name: "Relator",
            score: 65.3,
            description: "您享受與親近的人建立深厚的關係。"
          }
        ],
        message: "您的優勢分析已完成"
      }
    };
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