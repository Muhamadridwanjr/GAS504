import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

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
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('gas-token');
        localStorage.removeItem('gas-user');
    };

    return (
        <AuthContext.Provider value={{ user, token, saveSession, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
