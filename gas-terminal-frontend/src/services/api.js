import axios from 'axios';

// Use relative URL so Vite proxy handles it (no CORS, works from any host)
// Falls back to absolute URL only in production builds (served separately)
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/terminal';

const getHeaders = () => {
    const token = localStorage.getItem('gas-token') || '';
    return {
        'Authorization': `Bearer ${token}`
    };
};

// Billing & Checkout Services (direct to gas-billing-service via /billing-api proxy)
const BILLING_BASE = '/billing-api';

export const fetchBillingStatus = async (userId) => {
    try {
        const res = await fetch(`${BILLING_BASE}/api/v1/billing/status/${userId}`);
        return await res.json();
    } catch (err) {
        console.error("Failed to fetch billing status", err);
        return null;
    }
};

export const fetchTiers = async () => {
    try {
        const res = await fetch(`${BILLING_BASE}/api/v1/billing/tiers`);
        return await res.json();
    } catch (err) {
        console.error("Failed to fetch tiers", err);
        return {};
    }
};

export const subscribeTier = async (userId, tier, cycle = 'monthly') => {
    try {
        const res = await fetch(`${BILLING_BASE}/api/v1/checkout/subscribe?user_id=${userId}&tier=${tier}&cycle=${cycle}`, {
            method: 'POST'
        });
        return await res.json();
    } catch (err) {
        console.error("Subscription failed", err);
        return { status: 'error' };
    }
};

export const buyBooster = async (userId, packId) => {
    try {
        const res = await fetch(`${BILLING_BASE}/api/v1/checkout/buy-booster?user_id=${userId}&pack_id=${packId}`, {
            method: 'POST'
        });
        return await res.json();
    } catch (err) {
        console.error("Booster purchase failed", err);
        return { status: 'error' };
    }
};

export const fetchOverview = async () => {
    const res = await axios.get(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.data;
};

export const fetchPairs = async () => {
    const res = await axios.get(`${API_BASE}/pairs`, { headers: getHeaders() });
    return res.data;
};

export const fetchLatestSignal = async (pair) => {
    const res = await axios.get(`${API_BASE}/signal/latest`, {
        params: { pair },
        headers: getHeaders()
    });
    return res.data;
};

export const fetchNews = async () => {
    const res = await axios.get(`${API_BASE}/news`, { headers: getHeaders() });
    return res.data;
};

export const fetchCalendar = async (params = {}) => {
    const res = await axios.get(`${API_BASE}/calendar`, { params, headers: getHeaders() });
    return res.data;
};

export const fetchChartData = async (symbol, timeframe = 'M15', count = 100, indicators = []) => {
    const res = await axios.post(`${API_BASE}/chart/${symbol}/data`, {
        timeframe,
        count,
        indicators,
        include_smc: false
    }, { headers: getHeaders() });
    return res.data;
};

export const saveUserPreferences = async (prefs) => {
    const res = await axios.post(`${API_BASE}/user/preferences`, prefs, { headers: getHeaders() });
    return res.data;
};

export const fetchUserPreferences = async () => {
    const res = await axios.get(`${API_BASE}/user/preferences`, { headers: getHeaders() });
    return res.data;
};

export const sendAIChat = async (prompt, type = 'general', model_id = null) => {
    // Support object-style call: sendAIChat({ prompt, type, model_id })
    if (typeof prompt === 'object' && prompt !== null) {
        ({ prompt, type = 'general', model_id = null } = prompt);
    }
    const body = { prompt, type };
    if (model_id) body.model_id = model_id;
    const res = await axios.post(`${API_BASE}/ai/chat`, body, { headers: getHeaders() });
    return res.data;
};
