import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function AuthCallback() {
    const { saveSession } = useAuth();

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const token = params.get('token');
        const email = params.get('email');
        const name = params.get('name');
        const avatar = params.get('avatar');

        if (token && email) {
            saveSession(token, { email, full_name: name, avatar_url: avatar });
            // Clean URL and go to home
            window.history.replaceState({}, '', '/');
        } else {
            window.location.href = '/';
        }
    }, []);

    return null;
}
