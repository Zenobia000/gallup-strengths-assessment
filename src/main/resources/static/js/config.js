/**
 * Configuration Service - Gallup Strengths Assessment
 * Handles environment-specific configurations including API endpoints
 * Version: 1.0
 */

class Config {
  constructor() {
    this.env = this._detectEnvironment();
    this.config = this._getConfig();
  }

  /**
   * Detect current environment based on hostname
   * @returns {string} Environment name
   */
  _detectEnvironment() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    const port = window.location.port;

    // Development environment
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'development';
    }

    // Production environment
    if (hostname.includes('gallup-strengths') || hostname.includes('herokuapp')) {
      return 'production';
    }

    // Default to development
    return 'development';
  }

  /**
   * Get configuration based on environment
   * @returns {Object} Configuration object
   */
  _getConfig() {
    const configs = {
      development: {
        api: {
          baseURL: this._getDevApiUrl(),
          timeout: 10000,
          retries: 3
        },
        features: {
          debug: true,
          analytics: false,
          errorReporting: false
        },
        ui: {
          showDebugInfo: true,
          animationDuration: 300
        }
      },
      production: {
        api: {
          baseURL: this._getProdApiUrl(),
          timeout: 15000,
          retries: 5
        },
        features: {
          debug: false,
          analytics: true,
          errorReporting: true
        },
        ui: {
          showDebugInfo: false,
          animationDuration: 200
        }
      }
    };

    return configs[this.env] || configs.development;
  }

  /**
   * Get development API URL - auto-detect from current page
   * @returns {string} API base URL
   */
  _getDevApiUrl() {
    const currentOrigin = window.location.origin;

    // If we're on a specific port, try common API ports
    const apiPorts = [8002, 8000, 5000, 3001];

    // Extract current port
    const currentPort = window.location.port;

    // If current port is a known API port, use it
    if (apiPorts.includes(parseInt(currentPort))) {
      return `${currentOrigin}/api/v1`;
    }

    // Default to port 8002 for FastAPI
    return `${window.location.protocol}//${window.location.hostname}:8002/api/v1`;
  }

  /**
   * Get production API URL
   * @returns {string} API base URL
   */
  _getProdApiUrl() {
    // In production, API should be on same origin
    return `${window.location.origin}/api/v1`;
  }

  /**
   * Get API configuration
   * @returns {Object} API config
   */
  getApiConfig() {
    return this.config.api;
  }

  /**
   * Get API base URL
   * @returns {string} Base URL
   */
  getApiBaseURL() {
    return this.config.api.baseURL;
  }

  /**
   * Get feature flag
   * @param {string} feature - Feature name
   * @returns {boolean} Feature enabled status
   */
  isFeatureEnabled(feature) {
    return this.config.features[feature] || false;
  }

  /**
   * Get UI configuration
   * @returns {Object} UI config
   */
  getUIConfig() {
    return this.config.ui;
  }

  /**
   * Get current environment
   * @returns {string} Environment name
   */
  getEnvironment() {
    return this.env;
  }

  /**
   * Log configuration info (development only)
   */
  logInfo() {
    if (this.isFeatureEnabled('debug')) {
      console.group('🔧 Application Configuration');
      console.log('Environment:', this.env);
      console.log('API Base URL:', this.getApiBaseURL());
      console.log('Features:', this.config.features);
      console.log('UI Config:', this.config.ui);
      console.groupEnd();
    }
  }
}

// Export singleton instance
const config = new Config();
export { config };