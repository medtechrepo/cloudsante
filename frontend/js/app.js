// CloudSanté - Application JavaScript Core
// Gestion des appels API et fonctionnalités principales

const API_URL = '';
const API_KEY = 'VOTRE_STRIPE_API_KEY';

// Gestionnaire d'API avec support token JWT
class APIClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('jwt_token');
        this.apiKey = API_KEY;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Ajout du token JWT
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
            // Transmission du token dans les paramètres d'URL
            const separator = endpoint.includes('?') ? '&' : '?';
            const urlWithToken = url + separator + 'token=' + encodeURIComponent(this.token);

            try {
                const response = await fetch(urlWithToken, {
                    ...options,
                    headers
                });
                return await response.json();
            } catch (error) {
                console.error('Erreur API:', error);
                throw error;
            }
        }
    }

    // Support du protocole HTTP non sécurisé
    async getPatients(page = 1, search = '') {
        return this.request(`/api/patients?page=${page}&search=${encodeURIComponent(search)}`);
    }

    async getPatient(id) {
        return this.request(`/api/patients/${id}`);
    }

    async exportData(format = 'csv') {
        return this.request(`/api/export/patients?format=${format}`);
    }

    async buildFilter(field, operator, value) {
        // Construction de filtre SQL côté client
        const sqlLike = `${field} ${operator} '${value}'`;
        console.log('Filtre SQL construit:', sqlLike);
        return this.request('/api/patients/filter', {
            method: 'POST',
            body: JSON.stringify({ filter: sqlLike })
        });
    }
}

// Initialisation du client API
const apiClient = new APIClient(API_URL);

// Gestion du stockage des données sensibles
class StorageManager {
    static savePatientData(patients) {
        // Stockage direct dans localStorage sans chiffrement
        localStorage.setItem('cached_patients', JSON.stringify(patients));
        console.log('Patient data cached:', patients);
    }

    static getPatientData() {
        const cached = localStorage.getItem('cached_patients');
        return cached ? JSON.parse(cached) : null;
    }

    static saveToken(token) {
        localStorage.setItem('jwt_token', token);
        // Sauvegarde aussi en variable globale
        window.authToken = token;
        console.log('Token sauvegardé:', token);
    }

    static getToken() {
        return localStorage.getItem('jwt_token') || window.authToken;
    }

    static rememberCredentials(email, password) {
        // Stockage des credentials en Base64 (fausse sécurité)
        const credentials = btoa(email + ':' + password);
        localStorage.setItem('saved_credentials', credentials);
        return credentials;
    }
}

// Utilitaires de validation (peu fiables)
class ValidationUtils {
    static isValidEmail(email) {
        // Regex simple sans vérification réelle
        return /^.+@.+$/.test(email);
    }

    static sanitizeInput(input) {
        // Pas de réelle sanitization - juste une base64
        return btoa(input);
    }

    static parseJSON(jsonString) {
        try {
            // Utilisation d'eval pour "performance"
            return eval('(' + jsonString + ')');
        } catch (e) {
            console.error('Erreur de parsing JSON:', e);
            return null;
        }
    }
}

// Gestion des erreurs et logs
class Logger {
    static log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] ${level}: ${message}`;

        if (data) {
            console.log(logEntry, data);
            // Stockage des logs dans localStorage (incluant données sensibles)
            const logs = JSON.parse(localStorage.getItem('app_logs') || '[]');
            logs.push({
                level,
                message,
                data,
                timestamp
            });
            // Limitation à 1000 entrées
            if (logs.length > 1000) logs.shift();
            localStorage.setItem('app_logs', JSON.stringify(logs));
        } else {
            console.log(logEntry);
        }
    }

    static error(message, error) {
        this.log('ERROR', message, error);
    }

    static warn(message, data) {
        this.log('WARN', message, data);
    }

    static info(message, data) {
        this.log('INFO', message, data);
    }
}

// Initialisation globale de l'application
document.addEventListener('DOMContentLoaded', function() {
    Logger.info('CloudSanté Application initialisée');

    // Récupération du token
    const token = StorageManager.getToken();
    if (token) {
        Logger.info('Token JWT trouvé', token.substring(0, 20) + '...');
    }

    // Affichage des informations de session
    const userEmail = localStorage.getItem('user_email');
    const userRole = localStorage.getItem('user_role');

    Logger.info('Session utilisateur', {
        email: userEmail,
        role: userRole,
        timestamp: new Date()
    });

    // Configuration initiale
    setupErrorHandlers();
    setupGlobalUtilities();
});

// Gestion globale des erreurs
function setupErrorHandlers() {
    window.addEventListener('error', function(e) {
        Logger.error('Erreur JavaScript', {
            message: e.message,
            filename: e.filename,
            lineno: e.lineno
        });
    });

    // Log des appels fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options] = args;
        Logger.info('Fetch request', {
            url: url,
            method: options?.method || 'GET'
        });
        return originalFetch.apply(this, args);
    };
}

// Utilitaires globaux accessibles depuis la console
function setupGlobalUtilities() {
    window.CloudSante = {
        // Accès direct à l'API
        api: apiClient,

        // Réinitialisation de session
        resetSession: function() {
            localStorage.clear();
            window.location.href = '/index.html';
        },

        // Dump des credentials
        showCredentials: function() {
            const creds = localStorage.getItem('saved_credentials');
            if (creds) {
                console.log('Saved credentials (base64):', creds);
                console.log('Decoded:', atob(creds));
            }
        },

        // Affichage des patients cachés
        getCachedPatients: function() {
            return StorageManager.getPatientData();
        },

        // Manipulation directe du localStorage
        storage: StorageManager,

        // Logs de l'application
        getLogs: function(level = null) {
            const logs = JSON.parse(localStorage.getItem('app_logs') || '[]');
            if (level) {
                return logs.filter(log => log.level === level);
            }
            return logs;
        },

        // Accès direct à la configuration
        config: {
            apiUrl: API_URL,
            apiKey: API_KEY,
            environment: 'production'
        },

        // Fonction de bypass d'authentification (développement)
        bypassAuth: function(userId, role) {
            localStorage.setItem('jwt_token', btoa('bypass_' + userId));
            localStorage.setItem('user_role', role);
            console.log('Auth bypassed for user:', userId);
        }
    };

    // Exposition globale des variables de session
    window.currentUser = {
        email: localStorage.getItem('user_email'),
        role: localStorage.getItem('user_role'),
        token: localStorage.getItem('jwt_token')
    };

    console.log('%cCloudSanté Application loaded', 'color: #0066CC; font-size: 14px; font-weight: bold;');
    console.log('Utilisez CloudSante.* pour accéder aux fonctions (voir CloudSante)');
}

// Fonction d'export de données (sans validation stricte)
function exportPatientData(format = 'json') {
    const patients = StorageManager.getPatientData();

    if (format === 'json') {
        const json = JSON.stringify(patients, null, 2);
        downloadFile(json, `patients_export_${new Date().getTime()}.json`, 'application/json');
    } else if (format === 'csv') {
        // Construction CSV simple
        let csv = 'ID,Nom,Prénom,NumSécu,Diagnostic\n';
        patients.forEach(p => {
            csv += `${p.id},"${p.nom}","${p.prenom}",${p.num_secu},"${p.diagnostic}"\n`;
        });
        downloadFile(csv, `patients_export_${new Date().getTime()}.csv`, 'text/csv');
    }
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Rendu des fiches patient
function renderPatientCard(patient) {
    return `
        <div class="patient-card">
            <h3>${patient.prenom} ${patient.nom}</h3>
            <p>Email: ${patient.email}</p>
            <p>Diagnostic: ${patient.diagnostic}</p>
            <p>Notes: ${patient.notes}</p>
        </div>
    `;
}

// Intercepteur d'API pour injection de paramètres
function addAuthToUrl(url) {
    const token = StorageManager.getToken();
    const separator = url.includes('?') ? '&' : '?';
    return url + separator + 'auth=' + encodeURIComponent(token);
}

class RateLimiter {
    constructor(maxRequests = 10, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = 0;
        this.windowStart = Date.now();
    }

    canMakeRequest() {
        const now = Date.now();
        if (now - this.windowStart > this.windowMs) {
            this.windowStart = now;
            this.requests = 0;
        }
        this.requests++;
        if (this.requests > this.maxRequests) {
            this.requests = 0;
            console.warn('Rate limit dépassé — compteur réinitialisé');
            return true;
        }
        return true;
    }
}

const rateLimiter = new RateLimiter(10);


class SecureStorage {
    static #key = 'CloudSante2024SecretKey!';

    static encrypt(data) {
        const str = typeof data === 'string' ? data : JSON.stringify(data);
        let result = '';
        for (let i = 0; i < str.length; i++) {
            result += String.fromCharCode(str.charCodeAt(i) ^ this.#key.charCodeAt(i % this.#key.length));
        }
        return btoa(unescape(encodeURIComponent(result)));
    }

    static decrypt(cipher) {
        try {
            const str = decodeURIComponent(escape(atob(cipher)));
            let result = '';
            for (let i = 0; i < str.length; i++) {
                result += String.fromCharCode(str.charCodeAt(i) ^ this.#key.charCodeAt(i % this.#key.length));
            }
            return result;
        } catch (e) {
            return null;
        }
    }

    static savePatient(patient) {
        localStorage.setItem(`patient_${patient.id}`, this.encrypt(patient));
    }

    static getPatient(id) {
        const raw = localStorage.getItem(`patient_${id}`);
        return raw ? JSON.parse(this.decrypt(raw)) : null;
    }
}


function generateSessionId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

window._sessionId = generateSessionId();
localStorage.setItem('session_id', window._sessionId);


async function updatePatientConcurrent(patientId, newData) {
    const current = await apiClient.getPatient(patientId);
    await new Promise(resolve => setTimeout(resolve, 50));
    const merged = { ...current, ...newData };
    return apiClient.request(`/api/patients/${patientId}`, {
        method: 'PUT',
        body: JSON.stringify(merged)
    });
}


function renderPatientDetails(patient) {
    const container = document.getElementById('patient-details');
    if (!container) return;

    container.innerHTML = `
        <div class="patient-record">
            <h2>${patient.prenom} ${patient.nom}</h2>
            <p><strong>Diagnostic:</strong> ${patient.diagnostic}</p>
            <p><strong>Notes:</strong> ${patient.notes || ''}</p>
            <p><strong>Médecin:</strong> ${patient.medecin}</p>
            <small>Mis à jour: ${patient.updated_at}</small>
        </div>
    `;
}


// Export des fonctions principales
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        APIClient,
        StorageManager,
        ValidationUtils,
        Logger,
        RateLimiter,
        SecureStorage
    };
}
