/**
 * Healthcare Triage - Configuration
 * Centralized configuration for the frontend application
 * 
 * The API URL is determined dynamically based on the environment:
 * 1. Meta tag <meta name="api-url" content="...">
 * 2. Environment detection (localhost = development, else production)
 * 3. Fallback to localhost for development
 */

// Detect environment and set API URL
const detectApiUrl = () => {
    // Priority 1: Check for meta tag override
    const metaApiUrl = document.querySelector('meta[name="api-url"]')?.content;
    if (metaApiUrl) {
        return metaApiUrl;
    }

    // Priority 2: Environment-based detection
    const hostname = window.location.hostname;

    // Local development environments
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    // Production environment - configure your backend URL here
    // For ignite.gowshik.online, update this to your actual backend URL
    const productionApiUrls = {
        'ignite.gowshik.online': 'https://api.gowshik.online',  // Update with your actual backend URL
        // Add more domain mappings as needed
    };

    if (productionApiUrls[hostname]) {
        return productionApiUrls[hostname];
    }

    // Fallback: Assume API is on same origin with /api prefix
    // Or use a default backend URL
    return window.location.origin;
};

const CONFIG = {
    // API Configuration - dynamically detected
    API_BASE_URL: detectApiUrl(),

    // Application Settings
    APP_NAME: 'HealthCare AI',
    APP_VERSION: '1.0.0',

    // Token Settings
    TOKEN_KEY: 'token',
    USER_KEY: 'user',

    // Routes
    ROUTES: {
        LOGIN: 'index.html',
        LANDING: 'landing.html',
        PATIENT_DASHBOARD: 'patient-dashboard.html',
        DOCTOR_DASHBOARD: 'doctor-dashboard.html',
        ADMIN_DASHBOARD: 'admin.html'
    },

    // Environment detection
    IS_PRODUCTION: !['localhost', '127.0.0.1'].includes(window.location.hostname),

    // Debug logging (disable in production)
    DEBUG: ['localhost', '127.0.0.1'].includes(window.location.hostname)
};

// Log configuration in development
if (CONFIG.DEBUG) {
    console.log('🔧 Config loaded:', {
        API_BASE_URL: CONFIG.API_BASE_URL,
        IS_PRODUCTION: CONFIG.IS_PRODUCTION,
        hostname: window.location.hostname
    });
}

// Export for use in modules
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
