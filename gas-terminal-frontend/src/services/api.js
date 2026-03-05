import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8085/terminal';

// Retrieve token/user info (mocked for now)
const getHeaders = () => {
    const token = localStorage.getItem('token') || 'mock-token';
    return {
        'X-User-ID': 'dummy-user-123',
        'Authorization': `Bearer ${token}`
    };
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

export const fetchChartData = async (symbol, timeframe = 'M15', count = 100) => {
    // Call the MT5 data history proxy
    const res = await axios.get(`${API_BASE}/chart/${symbol}/history`, {
        params: { timeframe, count },
        headers: getHeaders()
    });
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
