/**
 * Healthcare Triage - Configuration
 * Centralized configuration for the frontend application
 */

const CONFIG = {
    // API Configuration
    // Change this URL based on your environment
    API_BASE_URL: 'http://localhost:8000',

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
    }
};

// Export for use in modules
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
