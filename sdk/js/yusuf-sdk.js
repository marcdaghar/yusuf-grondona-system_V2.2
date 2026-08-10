```javascript
/**
 * Yusuf-Grondona SDK – JavaScript/Node.js
 * ========================================
 *
 * SDK officiel pour l'intégration des partenaires BRI.
 *
 * Installation:
 *     npm install yusuf-grondona-sdk
 *
 * Usage:
 *     const { YusufGrondonaSDK } = require('yusuf-grondona-sdk');
 *     const sdk = new YusufGrondonaSDK('your_api_key');
 *     const rate = await sdk.getExchangeRate('Chine', 'France', 1000);
 *
 * License: CC BY-SA 4.0 – Marc Daghar
 */

const axios = require('axios');

class YusufGrondonaSDK {
    /**
     * @param {string} apiKey - Clé API pour l'authentification
     * @param {string} baseUrl - URL de base de l'API
     * @param {number} timeout - Timeout en millisecondes
     */
    constructor(
        apiKey,
        baseUrl = 'https://api.yusuf-grondona.com',
        timeout = 30000
    ) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.timeout = timeout;

        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: this.timeout,
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Yusuf-Grondona-SDK/1.0.0'
            }
        });
    }

    /**
     * Effectue une requête HTTP
     * @param {string} method - Méthode HTTP
     * @param {string} endpoint - Endpoint de l'API
     * @param {Object} data - Données pour POST/PUT
     * @param {Object} params - Paramètres pour GET
     * @returns {Promise<Object>} Réponse de l'API
     */
    async _request(method, endpoint, data = null, params = null) {
        try {
            const config = {
                method,
                url: endpoint,
                params
            };
            if (data) {
                config.data = data;
            }
            const response = await this.client.request(config);
            return response.data;
        } catch (error) {
            if (error.response) {
                return {
                    error: error.response.data?.message || error.message,
                    status: error.response.status,
                    message: 'Request failed'
                };
            }
            return {
                error: error.message,
                status: 'failed',
                message: 'Request failed'
            };
        }
    }

    // ---- Endpoints publics ----

    /**
     * Vérifie la disponibilité de l'API
     * @returns {Promise<Object>} Statut de l'API
     */
    async healthCheck() {
        return this._request('GET', '/api/v1/health');
    }

    /**
     * Obtient le taux de change entre deux zones BRI
     * @param {string} fromZone - Zone source
     * @param {string} toZone - Zone destination
     * @param {number} amount - Montant en fulus
     * @returns {Promise<Object>} Taux de change
     */
    async getExchangeRate(fromZone, toZone, amount) {
        return this._request('POST', '/api/v1/exchange_rate', {
            from_zone: fromZone,
            to_zone: toZone,
            amount_fulus: amount
        });
    }

    /**
     * Récupère le score ESG d'un partenaire
     * @param {string} partnerId - ID du partenaire
     * @param {number} year - Année
     * @returns {Promise<Object>} Score ESG
     */
    async getESGScore(partnerId, year = 2026) {
        return this._request('GET', `/api/v1/esg/${partnerId}`, null, { year });
    }

    /**
     * Récupère les prix du CRD
     * @returns {Promise<Object>} Prix des commodités
     */
    async getCRDPrices() {
        return this._request('GET', '/api/v1/crd/prices');
    }

    /**
     * Enregistre une transaction BRI
     * @param {string} partnerId - ID du partenaire
     * @param {string} txType - Type de transaction
     * @param {number} amount - Montant
     * @param {string} currency - Devise
     * @param {string} reference - Référence
     * @returns {Promise<Object>} ID de transaction
     */
    async recordTransaction(partnerId, txType, amount, currency = 'fulus', reference = null) {
        return this._request('POST', '/api/v1/transactions/record', {
            partner_id: partnerId,
            tx_type: txType,
            amount,
            currency,
            reference
        });
    }

    /**
     * Récupère le taux de Zakat
     * @returns {Promise<Object>} Taux de Zakat
     */
    async getZakatRate() {
        return this._request('GET', '/api/v1/zakat/rate');
    }

    // ---- Endpoints protégés ----

    /**
     * Récupère les métriques économiques globales
     * @returns {Promise<Object>} Métriques
     */
    async getMetrics() {
        return this._request('GET', '/secure/metrics');
    }

    /**
     * Lance une simulation
     * @param {Object} options - Options de simulation
     * @returns {Promise<Object>} Résultats
     */
    async runSimulation(options = {}) {
        const {
            years = 1,
            use_crd = true,
            use_zakat = true,
            use_bri = true
        } = options;

        return this._request('POST', '/run', {
            years,
            use_crd,
            use_zakat,
            use_bri
        });
    }

    /**
     * Effectue un transfert de nuqud
     * @param {string} fromZone - Zone source
     * @param {string} toZone - Zone destination
     * @param {number} amount - Montant en grammes d'or
     * @returns {Promise<Object>} Résultat du transfert
     */
    async transferNuqud(fromZone, toZone, amount) {
        return this._request('POST', '/transfer', {
            from_zone: fromZone,
            to_zone: toZone,
            amount_nuqud: amount
        });
    }

    // ---- Webhooks ----

    /**
     * S'abonne à des webhooks
     * @param {string} partnerId - ID du partenaire
     * @param {string} url - URL du webhook
     * @param {string[]} events - Événements
     * @param {string} secret - Secret HMAC
     * @returns {Promise<Object>} Statut
     */
    async subscribeWebhook(partnerId, url, events, secret) {
        return this._request('POST', '/api/webhooks/subscribe', {
            partner_id: partnerId,
            url,
            events,
            secret
        });
    }

    /**
     * Se désabonne d'un webhook
     * @param {string} partnerId - ID du partenaire
     * @param {string} url - URL du webhook
     * @returns {Promise<Object>} Statut
     */
    async unsubscribeWebhook(partnerId, url) {
        return this._request('DELETE', '/api/webhooks/unsubscribe', null, {
            partner_id: partnerId,
            url
        });
    }

    /**
     * Liste les abonnements webhook
     * @param {string} partnerId - ID du partenaire
     * @returns {Promise<Object>} Liste des abonnements
     */
    async getWebhookSubscriptions(partnerId) {
        return this._request('GET', '/api/webhooks/subscriptions', null, {
            partner_id: partnerId
        });
    }
}

// Export pour Node.js et ES modules
module.exports = { YusufGrondonaSDK };
