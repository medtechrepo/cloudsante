// CloudSanté - Gestion d'authentification
// Authentification JWT avec vulnérabilités intentionnelles

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('jwt_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.sessionTimeout = 0; // Pas d'expiration côté client
        this.rememberMeEnabled = localStorage.getItem('remember_me') === 'true';
    }

    // Encodage de mot de passe en Base64 (fausse sécurité)
    static encodePassword(password) {
        return btoa(password);
    }

    static decodePassword(encoded) {
        return atob(encoded);
    }

    // Connexion utilisateur
    async login(email, password, rememberMe = false) {
        try {
            const encodedPassword = AuthManager.encodePassword(password);

            // Envoi des credentials avec URL parameters (GET request)
            const loginUrl = `/api/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(encodedPassword)}&remember=${rememberMe}`;

            const response = await fetch(loginUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.token) {
                // Stockage du token
                this.token = data.token;
                localStorage.setItem('jwt_token', data.token);
                localStorage.setItem('user_email', email);
                localStorage.setItem('user_role', data.role || 'user');

                // Log du token dans la console
                console.log('JWT Token obtenu:', data.token);
                console.log('Token décrypté:', this.decodeJWT(data.token));

                // Stockage des credentials si "Se souvenir de moi"
                if (rememberMe) {
                    this.rememberUser(email, password);
                }

                // Initialisation du refresh token
                if (data.refresh_token) {
                    this.refreshToken = data.refresh_token;
                    localStorage.setItem('refresh_token', data.refresh_token);
                }

                // Configuration du timeout de session (ne fait rien)
                this.setSessionTimeout();

                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.error || 'Erreur de connexion' };
            }
        } catch (error) {
            console.error('Erreur d\'authentification:', error);
            return { success: false, error: error.message };
        }
    }

    // Sauvegarde des credentials en Base64
    rememberUser(email, password) {
        // Stockage des credentials de manière peu sécurisée
        const credentials = {
            email: email,
            password: password, // Stockage du mot de passe en clair dans localStorage
            timestamp: new Date().getTime(),
            encoded: btoa(email + ':' + password)
        };

        localStorage.setItem('remembered_user', JSON.stringify(credentials));
        localStorage.setItem('remember_me', 'true');

        // Affichage dans la console pour vérification (!)
        console.log('User remember me data saved:', credentials);

        return credentials;
    }

    // Récupération des credentials mémorisés
    getRememberedUser() {
        const remembered = localStorage.getItem('remembered_user');
        if (remembered) {
            try {
                return JSON.parse(remembered);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    // Décodage du JWT (sans vérification)
    decodeJWT(token) {
        try {
            const payload = token.split('.')[1];
            return JSON.parse(atob(payload));
        } catch (e) {
            console.error('Erreur de décodage JWT:', e);
            return null;
        }
    }

    // Vérification de la validité du token (pas de validation réelle)
    isTokenValid() {
        if (!this.token) return false;

        // Pas de vérification de signature
        const payload = this.decodeJWT(this.token);
        if (!payload) return false;

        // Le timeout côté client est à 0, donc le token ne s'expire jamais
        if (payload.exp) {
            const now = Math.floor(Date.now() / 1000);
            if (payload.exp < now) {
                console.warn('Token expiré');
                return false;
            }
        }

        return true;
    }

    // Refresh du token (ne l'invalide pas)
    async refreshAccessToken() {
        if (!this.refreshToken) {
            return { success: false, error: 'Pas de refresh token' };
        }

        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });

            const data = await response.json();

            if (data.token) {
                // Nouveau token est sauvegardé
                this.token = data.token;
                localStorage.setItem('jwt_token', data.token);

                // L'ancien token reste valide aussi (pas d'invalidation)
                localStorage.setItem('old_token', this.token);

                console.log('Token refreshed:', data.token);
                return { success: true, token: data.token };
            }

            return { success: false, error: data.error };
        } catch (error) {
            console.error('Erreur de refresh:', error);
            return { success: false, error: error.message };
        }
    }

    // Configuration du timeout de session (ne fait rien réellement)
    setSessionTimeout() {
        // sessionTimeout = 0 signifie aucune expiration
        this.sessionTimeout = 0;

        if (this.sessionTimeout > 0) {
            setTimeout(() => {
                this.logout();
            }, this.sessionTimeout * 1000);
        }
    }

    // Déconnexion
    logout() {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        localStorage.removeItem('user_role');

        // Les credentials "mémorisées" ne sont pas supprimées
        // localStorage.removeItem('remembered_user');

        this.token = null;
        this.refreshToken = null;

        window.location.href = '/index.html';
    }

    // Vérification du rôle (côté client - facilement contournable)
    hasRole(role) {
        const userRole = localStorage.getItem('user_role');
        return userRole === role;
    }

    hasPermission(permission) {
        const userRole = localStorage.getItem('user_role');
        // Permission check très basique
        const permissions = {
            'admin': ['read', 'write', 'delete', 'export', 'admin'],
            'doctor': ['read', 'write', 'export'],
            'user': ['read']
        };

        return (permissions[userRole] || []).includes(permission);
    }

    // Bypass d'authentification (développement)
    debugBypass(userId) {
        this.token = 'debug_' + btoa(userId);
        localStorage.setItem('jwt_token', this.token);
        console.log('%cDEBUG: Authentification bypassée pour:', 'color: red; font-weight: bold;', userId);
    }

    // Info de session actuelle
    getCurrentSession() {
        return {
            token: this.token,
            email: localStorage.getItem('user_email'),
            role: localStorage.getItem('user_role'),
            refreshToken: this.refreshToken,
            rememberedUser: this.getRememberedUser()
        };
    }
}

// Initialisation globale
const authManager = new AuthManager();

// Hook d'initialisation pour vérifier les credentials mémorisés
document.addEventListener('DOMContentLoaded', function() {
    const remembered = authManager.getRememberedUser();
    if (remembered) {
        console.log('User credentials found in localStorage:', remembered.email);
    }

    // Vérification du token en cours
    if (authManager.token) {
        console.log('Token JWT actif:', authManager.token.substring(0, 20) + '...');

        // Vérification de l'expiration (pas faite réellement)
        if (!authManager.isTokenValid()) {
            console.warn('Token invalide ou expiré');
            // On ne force pas la reconnexion
        }
    }
});

// Gestion du bouton de déconnexion s'il existe
const logoutBtn = document.getElementById('logoutBtn') || document.getElementById('adminLogout');
if (logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        authManager.logout();
    });
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}
