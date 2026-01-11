/**
 * Healthcare Triage - Chat Module
 * AI consultation chat interface logic
 */

const Chat = {
    sessionId: null,
    symptoms: [],

    // Initialize chat session
    async startSession() {
        try {
            const response = await window.API.triage.startSession();
            if (response.status === 'success') {
                this.sessionId = response.data.session_id;
                this.symptoms = response.data.symptoms_reported || [];
                return { success: true, sessionId: this.sessionId };
            }
            return { success: false, message: response.message };
        } catch (error) {
            console.error('Failed to start session:', error);
            return { success: false, message: error.message };
        }
    },

    // Add symptom to session
    async addSymptom(symptomId) {
        if (!this.sessionId) {
            await this.startSession();
        }

        try {
            const response = await window.API.triage.addSymptom(this.sessionId, symptomId);
            if (response.status === 'success') {
                this.symptoms = response.data.symptoms_reported;
                return { success: true, symptom: response.data.symptom_added };
            }
            return { success: false, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Get triage result
    async getResult() {
        if (!this.sessionId) {
            return { success: false, message: 'No active session' };
        }

        try {
            const response = await window.API.triage.getResult(this.sessionId);
            if (response.status === 'success') {
                return { success: true, result: response.data };
            }
            return { success: false, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Get available symptoms
    async getSymptomsList() {
        try {
            const response = await window.API.triage.getSymptoms();
            if (response.status === 'success') {
                return response.data.symptoms || [];
            }
            return [];
        } catch (error) {
            console.error('Failed to get symptoms:', error);
            return [];
        }
    },

    // Search symptoms
    searchSymptoms(query, symptomsList) {
        const lower = query.toLowerCase();
        return symptomsList.filter(s =>
            s.name.toLowerCase().includes(lower) ||
            (s.description && s.description.toLowerCase().includes(lower))
        );
    },

    // Generate AI response based on user message (demo mode)
    generateDemoResponse(message) {
        const lower = message.toLowerCase();

        if (lower.includes('headache')) {
            return {
                text: `I understand you're experiencing a headache. Let me ask a few questions:\n\n• How severe is the pain (1-10)?
• Is it constant or pulsating?
• Any other symptoms like nausea or light sensitivity?`,
                riskLevel: 'low'
            };
        }

        if (lower.includes('fever')) {
            return {
                text: `Fever can indicate your body is fighting an infection. 🌡️\n\n• What is your current temperature?
• How long have you had the fever?
• Any other symptoms like chills or body aches?`,
                riskLevel: 'medium'
            };
        }

        if (lower.includes('chest') && lower.includes('pain')) {
            return {
                text: `⚠️ Chest pain can be serious. Please answer:\n\n• Is the pain sharp or dull?
• Does it radiate to your arm or jaw?
• Are you having difficulty breathing?\n\n🚨 If severe, please call emergency services immediately.`,
                riskLevel: 'high'
            };
        }

        if (lower.includes('tired') || lower.includes('fatigue')) {
            return {
                text: `Fatigue and tiredness can have many causes:\n\n• How long have you been feeling this way?
• Are you getting enough sleep (7-9 hours)?
• Any recent changes in diet or stress levels?`,
                riskLevel: 'low'
            };
        }

        return {
            text: `Thank you for sharing that. Could you tell me more about:
        
1. When did this start?
2. How severe is it (1-10)?
3. Is it constant or does it come and go?

This will help me provide better guidance.`,
            riskLevel: 'unknown'
        };
    },

    // End session and get summary
    async endSession() {
        const result = await this.getResult();
        this.sessionId = null;
        this.symptoms = [];
        return result;
    }
};

window.Chat = Chat;
