/**
 * Local Storage Service - Gallup Strengths Assessment
 * Handles persistent data storage using localStorage
 * Version: 1.0
 */

class Storage {
  constructor() {
    this.prefix = 'gallup_';
    this.SESSION_KEY = 'session_id';
    this.CONSENT_KEY = 'consent_given';
    this.ANSWERS_KEY = 'answers';
    this.PROGRESS_KEY = 'progress';
    this.TIMESTAMP_KEY = 'timestamp';
  }

  /**
   * Get prefixed key
   * @param {string} key - Storage key
   * @returns {string} Prefixed key
   */
  getKey(key) {
    return `${this.prefix}${key}`;
  }

  /**
   * Set item in localStorage
   * @param {string} key - Storage key
   * @param {*} value - Value to store (will be JSON stringified)
   * @returns {boolean} Success status
   */
  set(key, value) {
    try {
      const prefixedKey = this.getKey(key);
      const data = JSON.stringify(value);
      localStorage.setItem(prefixedKey, data);
      return true;
    } catch (error) {
      console.error('Storage set error:', error);
      return false;
    }
  }

  /**
   * Get item from localStorage
   * @param {string} key - Storage key
   * @param {*} defaultValue - Default value if key doesn't exist
   * @returns {*} Stored value or defaultValue
   */
  get(key, defaultValue = null) {
    try {
      const prefixedKey = this.getKey(key);
      const data = localStorage.getItem(prefixedKey);

      if (data === null) {
        return defaultValue;
      }

      return JSON.parse(data);
    } catch (error) {
      console.error('Storage get error:', error);
      return defaultValue;
    }
  }

  /**
   * Remove item from localStorage
   * @param {string} key - Storage key
   * @returns {boolean} Success status
   */
  remove(key) {
    try {
      const prefixedKey = this.getKey(key);
      localStorage.removeItem(prefixedKey);
      return true;
    } catch (error) {
      console.error('Storage remove error:', error);
      return false;
    }
  }

  /**
   * Clear all app-related items from localStorage
   * @returns {boolean} Success status
   */
  clear() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key);
        }
      });
      return true;
    } catch (error) {
      console.error('Storage clear error:', error);
      return false;
    }
  }

  /**
   * Check if key exists
   * @param {string} key - Storage key
   * @returns {boolean}
   */
  has(key) {
    const prefixedKey = this.getKey(key);
    return localStorage.getItem(prefixedKey) !== null;
  }

  // ============================================
  // Session Management
  // ============================================

  /**
   * Save session ID
   * @param {string} sessionId - Session ID
   * @returns {boolean}
   */
  saveSession(sessionId) {
    const success = this.set(this.SESSION_KEY, sessionId);
    if (success) {
      this.set(this.TIMESTAMP_KEY, Date.now());
    }
    return success;
  }

  /**
   * Get session ID
   * @returns {string|null}
   */
  getSession() {
    return this.get(this.SESSION_KEY);
  }

  /**
   * Check if session exists and is valid (not expired)
   * @param {number} maxAge - Maximum age in milliseconds (default 24 hours)
   * @returns {boolean}
   */
  hasValidSession(maxAge = 24 * 60 * 60 * 1000) {
    const sessionId = this.getSession();
    if (!sessionId) return false;

    const timestamp = this.get(this.TIMESTAMP_KEY);
    if (!timestamp) return false;

    const age = Date.now() - timestamp;
    return age < maxAge;
  }

  /**
   * Clear session data
   * @returns {boolean}
   */
  clearSession() {
    this.remove(this.SESSION_KEY);
    this.remove(this.TIMESTAMP_KEY);
    this.remove(this.ANSWERS_KEY);
    this.remove(this.PROGRESS_KEY);
    return true;
  }

  // ============================================
  // Consent Management
  // ============================================

  /**
   * Save consent status
   * @param {boolean} given - Consent given status
   * @returns {boolean}
   */
  saveConsent(given) {
    return this.set(this.CONSENT_KEY, {
      given,
      timestamp: Date.now(),
    });
  }

  /**
   * Check if consent was given
   * @returns {boolean}
   */
  hasConsent() {
    const consent = this.get(this.CONSENT_KEY);
    return consent && consent.given === true;
  }

  /**
   * Get consent data
   * @returns {Object|null}
   */
  getConsent() {
    return this.get(this.CONSENT_KEY);
  }

  // ============================================
  // Answers Management
  // ============================================

  /**
   * Save answers
   * @param {Array} answers - Array of answer objects
   * @returns {boolean}
   */
  saveAnswers(answers) {
    return this.set(this.ANSWERS_KEY, answers);
  }

  /**
   * Get saved answers
   * @returns {Array}
   */
  getAnswers() {
    return this.get(this.ANSWERS_KEY, []);
  }

  /**
   * Save single answer
   * @param {number} questionId - Question ID
   * @param {number} score - Answer score
   * @returns {boolean}
   */
  saveAnswer(questionId, score) {
    const answers = this.getAnswers();
    const existingIndex = answers.findIndex(a => a.question_id === questionId);

    if (existingIndex >= 0) {
      answers[existingIndex] = { question_id: questionId, score };
    } else {
      answers.push({ question_id: questionId, score });
    }

    return this.saveAnswers(answers);
  }

  /**
   * Get answer for specific question
   * @param {number} questionId - Question ID
   * @returns {Object|null}
   */
  getAnswer(questionId) {
    const answers = this.getAnswers();
    return answers.find(a => a.question_id === questionId) || null;
  }

  // ============================================
  // Progress Management
  // ============================================

  /**
   * Save progress data
   * @param {Object} progress - Progress data (currentIndex, total, etc.)
   * @returns {boolean}
   */
  saveProgress(progress) {
    return this.set(this.PROGRESS_KEY, {
      ...progress,
      lastUpdated: Date.now(),
    });
  }

  /**
   * Get progress data
   * @returns {Object|null}
   */
  getProgress() {
    return this.get(this.PROGRESS_KEY);
  }

  /**
   * Clear progress data
   * @returns {boolean}
   */
  clearProgress() {
    return this.remove(this.PROGRESS_KEY);
  }

  // ============================================
  // Utility Methods
  // ============================================

  /**
   * Get all stored data (for debugging)
   * @returns {Object}
   */
  getAllData() {
    const data = {};
    const keys = Object.keys(localStorage);

    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        const originalKey = key.substring(this.prefix.length);
        data[originalKey] = this.get(originalKey);
      }
    });

    return data;
  }

  /**
   * Check storage availability
   * @returns {boolean}
   */
  isAvailable() {
    try {
      const testKey = '__storage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get storage usage (approximate)
   * @returns {number} Storage size in bytes
   */
  getUsage() {
    let size = 0;
    const keys = Object.keys(localStorage);

    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        const value = localStorage.getItem(key);
        size += key.length + (value ? value.length : 0);
      }
    });

    return size;
  }
}

// Export singleton instance
const storage = new Storage();
export { storage };