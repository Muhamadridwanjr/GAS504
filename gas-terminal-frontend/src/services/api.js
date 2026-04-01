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

export const fetchLiveNews = async () => {
    try {
        const res = await axios.get(`${API_BASE}/livenews`, { headers: getHeaders() });
        return res.data;
    } catch { return { news: [] }; }
};

export const fetchBreakingNews = async () => {
    try {
        const res = await axios.get(`${API_BASE}/breakingnews`, { headers: getHeaders() });
        return res.data;
    } catch { return { active: false, items: [] }; }
};

export const fetchMacro = async () => {
    const res = await axios.get(`${API_BASE}/fundamental/macro`, { headers: getHeaders() });
    return res.data;
};

export const fetchCalendar = async (params = {}) => {
    const res = await axios.get(`${API_BASE}/calendar`, { params, headers: getHeaders() });
    return res.data;
};

export const fetchCalendarAnalysis = async () => {
    try {
        const res = await axios.get(`${API_BASE}/calendar/analysis`, { headers: getHeaders() });
        return res.data;
    } catch (err) {
        console.error('fetchCalendarAnalysis error:', err);
        return { status: 'no_data', data: {} };
    }
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

// ── AI Feature Calls (all 18 features from gasfiturmap.md) ──────────────────
const WEB_API = '/web/api/v1';

export const callAIFeature = async (feature, params = {}) => {
    const res = await axios.post(`${WEB_API}/analysis/${feature}`, params, { headers: getHeaders(), timeout: 120000 });
    return res.data;
};

export const fetchSignalModels = async () => {
    const res = await axios.get(`${WEB_API}/analysis/signal/models`, { headers: getHeaders() });
    return res.data;
};

export const fetchUserCredits = async () => {
    const res = await axios.get(`${WEB_API}/billing/status`, { headers: getHeaders() });
    return res.data;
};

export const fetchBoosterPacks = async () => {
    const res = await axios.get(`${WEB_API}/booster/packs`, { headers: getHeaders() });
    return res.data;
};

export const purchaseBooster = async (packId) => {
    const res = await axios.post(`${WEB_API}/booster/purchase`, { pack_id: packId }, { headers: getHeaders() });
    return res.data;
};

export const fetchUserLevel = async () => {
    const res = await axios.get(`${WEB_API}/user/level`, { headers: getHeaders() });
    return res.data;
};

export const fetchFeatureAccess = async () => {
    const res = await axios.get(`${WEB_API}/plan/features`, { headers: getHeaders() });
    return res.data;
};

// ── Binance Crypto Market Data ────────────────────────────────────────────────
const BINANCE_API = '/terminal/binance';

export const fetchBinanceTicker = async (symbol) => {
    try {
        const encoded = encodeURIComponent(symbol);
        const res = await axios.get(`${BINANCE_API}/ticker/${encoded}`, { headers: getHeaders() });
        return res.data;
    } catch (err) {
        console.error('fetchBinanceTicker error:', err);
        return null;
    }
};

export const fetchBinanceTickers = async (symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'BNB/USDT']) => {
    try {
        const res = await axios.get(`${BINANCE_API}/tickers`, {
            params: { symbols: symbols.join(',') },
            headers: getHeaders()
        });
        // Normalize field names: binance-service returns `changePercent`, UI expects `percentage`
        const data = res.data || {};
        Object.values(data).forEach(t => {
            if (t && t.changePercent !== undefined && t.percentage === undefined) {
                t.percentage = t.changePercent;
            }
        });
        return data;
    } catch (err) {
        console.error('fetchBinanceTickers error:', err);
        return {};
    }
};

export const fetchBinanceSignal = async (symbol, timeframe = 'H1', limit = 200) => {
    try {
        const res = await axios.get(`${BINANCE_API}/analyze`, {
            params: { symbol, timeframe, limit },
            headers: getHeaders()
        });
        return res.data;
    } catch (err) {
        console.error('fetchBinanceSignal error:', err);
        throw err;
    }
};

export const fetchBinanceOHLCV = async (symbol, timeframe = '1h', limit = 100) => {
    try {
        const res = await axios.get(`${BINANCE_API}/ohlcv`, {
            params: { symbol, timeframe, limit },
            headers: getHeaders()
        });
        return res.data;
    } catch (err) {
        console.error('fetchBinanceOHLCV error:', err);
        return null;
    }
};

export const fetchBinanceOrderbook = async (symbol, limit = 10) => {
    try {
        const encoded = encodeURIComponent(symbol);
        const res = await axios.get(`${BINANCE_API}/orderbook/${encoded}`, {
            params: { limit },
            headers: getHeaders()
        });
        return res.data;
    } catch (err) {
        console.error('fetchBinanceOrderbook error:', err);
        return null;
    }
};

// ── Portfolio / MT5 Live Data ──────────────────────────────────────────────────
export const fetchPortfolioLive = async () => {
    try {
        const res = await axios.get(`${API_BASE}/portfolio/live`, { headers: getHeaders() });
        return res.data;
    } catch (err) {
        console.error('fetchPortfolioLive error:', err);
        return null;
    }
};

export const fetchOpenPositions = async () => {
    try {
        const res = await axios.get(`${API_BASE}/portfolio/positions`, { headers: getHeaders() });
        return res.data;
    } catch (err) {
        console.error('fetchOpenPositions error:', err);
        return { positions: [] };
    }
};

export const fetchAccountStatus = async () => {
    try {
        const res = await axios.get(`${API_BASE}/portfolio/account-status`, { headers: getHeaders() });
        return res.data;
    } catch (err) {
        console.error('fetchAccountStatus error:', err);
        return { mode: 'offline', has_user_ea: false, has_main_ea: false };
    }
};
