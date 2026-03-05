import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url, onMessage) {
    const ws = useRef(null);
    const onMessageRef = useRef(onMessage);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        onMessageRef.current = onMessage;
    }, [onMessage]);

    useEffect(() => {
        // Basic automatic reconnection loop (simplified)
        let reconnectTimeout = null;

        const connect = () => {
            if (!url) return;

            ws.current = new WebSocket(url);

            ws.current.onopen = () => {
                setIsConnected(true);
                console.log('WS Connected to:', url);
            };

            ws.current.onclose = () => {
                setIsConnected(false);
                console.log('WS Disconnected, retrying...');
                // Try to reconnect in 3s
                reconnectTimeout = setTimeout(connect, 3000);
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (onMessageRef.current) onMessageRef.current(data);
                } catch (err) {
                    console.error('WS Parse Error:', err);
                }
            };
        };

        connect();

        return () => {
            clearTimeout(reconnectTimeout);
            if (ws.current) {
                ws.current.onclose = null; // prevent reconnect on intentional unmount
                ws.current.close();
            }
        };
    }, [url]); // Intentionally not including onMessage to avoid reconnect on every render

    const send = (msg) => {
        if (ws.current && isConnected) {
            ws.current.send(JSON.stringify(msg));
        }
    };

    return { isConnected, send };
}
