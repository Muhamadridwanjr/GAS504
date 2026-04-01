import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Admin usernames that get full access (matches auth service)
const ADMIN_USERNAMES = ['admin', 'ridwanjr'];

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const savedToken = localStorage.getItem('gas-token');
        const savedUser = localStorage.getItem('gas-user');
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
        setLoading(false);
    }, []);

    const saveSession = (tokenValue, userData) => {
        setToken(tokenValue);
        setUser(userData);
        localStorage.setItem('gas-token', tokenValue);
        localStorage.setItem('gas-user', JSON.stringify(userData));
        // Fix URL — remove /login or /signup from address bar after auth
        if (window.location.pathname !== '/') {
            window.history.pushState({}, '', '/');
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('gas-token');
        localStorage.removeItem('gas-user');
    };

    // Derived values
    const isAdmin = !!(
        user?.role === 'admin' ||
        user?.is_admin === true ||
        (user?.username && ADMIN_USERNAMES.includes(user.username.toLowerCase()))
    );

    // Admin always gets ultimate plan (all 18 features)
    // Default to 'free' so paid plans are purchasable by users without a plan set
    const userPlan = isAdmin ? 'ultimate' : (user?.plan || 'free');

    // Features accessible by plan
    const PLAN_FEATURES = {
        free:      ['signal'],  // minimal free access
        essential: ['technical', 'signal', 'alert', 'session'],
        plus:      ['technical', 'signal', 'alert', 'session', 'correlation', 'fundamental', 'calendar', 'sentiment', 'risk'],
        premium:   ['technical', 'signal', 'alert', 'session', 'correlation', 'fundamental', 'calendar', 'sentiment', 'risk', 'hybrid', 'drawdown', 'briefing', 'psychology', 'journal', 'propfirm'],
        ultimate:  ['technical', 'signal', 'alert', 'session', 'correlation', 'fundamental', 'calendar', 'sentiment', 'risk', 'hybrid', 'drawdown', 'briefing', 'psychology', 'journal', 'propfirm', 'scanner', 'backtesting', 'mentor'],
    };

    const canAccess = (feature) => {
        if (isAdmin) return true;
        return (PLAN_FEATURES[userPlan] || PLAN_FEATURES.free).includes(feature);
    };

    // Credit cost per message in mentor chat based on plan model
    const PLAN_CHAT_CREDIT = { essential: 3, plus: 3, premium: 5, ultimate: 5 };
    const chatCreditCost = PLAN_CHAT_CREDIT[userPlan] || 3;

    // AI model for mentor chat based on plan
    const PLAN_CHAT_MODEL = {
        essential: { id: 'gpt-5-mini',        label: 'GPT-5 Mini' },
        plus:      { id: 'gemini-3-flash',     label: 'Gemini 3 Flash' },
        premium:   { id: 'claude-haiku-4.5',   label: 'Claude Haiku 4.5' },
        ultimate:  { id: 'claude-sonnet-4.6',  label: 'Claude Sonnet 4.6' },
    };
    const chatModel = isAdmin
        ? { id: 'claude-opus-4.6', label: 'Claude Opus 4.6 (Admin)' }
        : (PLAN_CHAT_MODEL[userPlan] || PLAN_CHAT_MODEL.essential);

    return (
        <AuthContext.Provider value={{
            user,
            token,
            saveSession,
            logout,
            loading,
            isAdmin,
            userPlan,
            canAccess,
            chatCreditCost,
            chatModel,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
