import axios from 'axios';

const AUTH_BASE = '/auth/v1/auth';

export const getGoogleLoginUrl = async () => {
    const res = await axios.get(`${AUTH_BASE}/google`);
    return res.data.url;
};

export const logoutApi = async (token) => {
    // Local JWT — just clear client-side storage (no server call needed)
};
