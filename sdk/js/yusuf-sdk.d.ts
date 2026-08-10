/**
 * Yusuf-Grondona SDK – TypeScript Declarations
 */

export interface ExchangeRateResponse {
    from: string;
    to: string;
    amount: number;
    converted: number;
    rate: number;
    timestamp: number;
}

export interface ESGScoreResponse {
    partner: string;
    year: number;
    esg: {
        environmental: number;
        social: number;
        governance: number;
        global: number;
    };
    last_update: number;
}

export interface CRDPricesResponse {
    wheat: { floor: number; ceiling: number; current: number };
    copper: { floor: number; ceiling: number; current: number };
    salt: { floor: number; ceiling: number; current: number };
    rice: { floor: number; ceiling: number; current: number };
    timestamp: number;
}

export interface TransferResponse {
    success: boolean;
    from: string;
    to: string;
    gross: number;
    fee: number;
    net: number;
    timestamp: number;
}

export interface TransactionRecordResponse {
    status: string;
    tx_id: string;
    partner: string;
    timestamp: number;
}

export class YusufGrondonaSDK {
    constructor(apiKey: string, baseUrl?: string, timeout?: number);

    // Public endpoints
    healthCheck(): Promise<{ status: string; timestamp: number }>;
    getExchangeRate(fromZone: string, toZone: string, amount: number): Promise<ExchangeRateResponse>;
    getESGScore(partnerId: string, year?: number): Promise<ESGScoreResponse>;
    getCRDPrices(): Promise<CRDPricesResponse>;
    recordTransaction(
        partnerId: string,
        txType: string,
        amount: number,
        currency?: string,
        reference?: string
    ): Promise<TransactionRecordResponse>;
    getZakatRate(): Promise<{ zakat_rate: number; nisab_gold_grams: number; nisab_silver_grams: number }>;

    // Protected endpoints
    getMetrics(): Promise<Record<string, any>>;
    runSimulation(options?: {
        years?: number;
        use_crd?: boolean;
        use_zakat?: boolean;
        use_bri?: boolean;
    }): Promise<Record<string, any>>;
    transferNuqud(fromZone: string, toZone: string, amount: number): Promise<TransferResponse>;

    // Webhooks
    subscribeWebhook(partnerId: string, url: string, events: string[], secret: string): Promise<{ status: string }>;
    unsubscribeWebhook(partnerId: string, url: string): Promise<{ status: string }>;
    getWebhookSubscriptions(partnerId: string): Promise<{ partner: string; subscriptions: Array<{ url: string; events: string[] }> }>;
}
