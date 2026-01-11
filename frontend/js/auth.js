/**
 * Healthcare Triage - Authentication Module
 * Handles login, signup, session management, and JWT tokens
 */

const Auth = {
    // Check if user is logged in
    isAuthenticated() {
        return !!localStorage.getItem('token');
    },

    // Get current user data
    getUser() {
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) : null;
    },

    // Get token
    getToken() {
        return localStorage.getItem('token');
    },

    // Save auth data
    saveAuth(token, user) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    },

    // Clear auth data
    clearAuth() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    // Login
    async login(email, password) {
        try {
            const response = await window.API.auth.login(email, password);
            if (response.status === 'success' && response.data) {
                this.saveAuth(response.data.access_token, response.data.user);
                return { success: true, user: response.data.user };
            }
            return { success: false, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Register
    async register(userData) {
        try {
            const response = await window.API.auth.register(userData);
            if (response.status === 'success' && response.data) {
                this.saveAuth(response.data.access_token, response.data.user);
                return { success: true, user: response.data.user };
            }
            return { success: false, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Logout
    logout() {
        this.clearAuth();
        window.location.href = 'index.html';
    },

    // Check role
    hasRole(role) {
        const user = this.getUser();
        return user && user.role === role;
    },

    // Redirect based on role
    redirectToDashboard() {
        const user = this.getUser();
        if (!user) {
            window.location.href = 'index.html';
            return;
        }

        switch (user.role) {
            case 'doctor':
                window.location.href = 'doctor-dashboard.html';
                break;
            case 'admin':
                window.location.href = 'admin.html';
                break;
            default:
                window.location.href = 'patient-dashboard.html';
        }
    },

    // Protect page - redirect if not authenticated
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    },

    // Protect page - require specific role
    requireRole(role) {
        if (!this.requireAuth()) return false;
        if (!this.hasRole(role)) {
            this.redirectToDashboard();
            return false;
        }
        return true;
    }
};

// Form handlers for login page
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';

            const result = await Auth.login(email, password);

            if (result.success) {
                Utils.showToast('Login successful!', 'success');
                setTimeout(() => Auth.redirectToDashboard(), 1000);
            } else {
                Utils.showToast(result.message || 'Login failed', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign In';
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('signup-name').value;
            const email = document.getElementById('signup-email').value;
            const phone = document.getElementById('signup-phone').value;
            const password = document.getElementById('signup-password').value;
            const role = document.querySelector('input[name="role"]:checked').value;

            const submitBtn = signupForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';

            const result = await Auth.register({ name, email, phone, password, role });

            if (result.success) {
                Utils.showToast('Account created!', 'success');
                setTimeout(() => Auth.redirectToDashboard(), 1000);
            } else {
                Utils.showToast(result.message || 'Registration failed', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        });
    }
});

window.Auth = Auth;
