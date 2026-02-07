import { useEffect, useRef, useState, useCallback } from "react";

interface WebSocketMessage {
    type: string;
    data: any;
}

interface UseWebSocketOptions {
    onMessage?: (message: WebSocketMessage) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Error) => void;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
}

export function useWebSocket(url: string | null, options: UseWebSocketOptions = {}) {
    const {
        onMessage,
        onConnect,
        onDisconnect,
        onError,
        reconnectInterval = 3000,
        maxReconnectAttempts = 5,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [reconnectAttempt, setReconnectAttempt] = useState(0);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
    const shouldConnectRef = useRef(true);

    const disconnect = useCallback(() => {
        shouldConnectRef.current = false;
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    const connect = useCallback(() => {
        // Prevent multiple connections
        if (!url || !shouldConnectRef.current) return;
        if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
            return;
        }

        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                if (!shouldConnectRef.current) {
                    ws.close();
                    return;
                }
                console.log('WebSocket connected');
                setIsConnected(true);
                setReconnectAttempt(0);
                onConnect?.();
            };

            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data);
                    onMessage?.(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                onError?.(error as any);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                wsRef.current = null;
                onDisconnect?.();

                // Attempt reconnection only if we should still be connected
                if (shouldConnectRef.current && reconnectAttempt < maxReconnectAttempts) {
                    reconnectTimeoutRef.current = setTimeout(() => {
                        console.log(`Reconnecting... (attempt ${reconnectAttempt + 1})`);
                        setReconnectAttempt((prev) => prev + 1);
                        connect();
                    }, reconnectInterval);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }, [url, reconnectAttempt, maxReconnectAttempts, reconnectInterval, onConnect, onMessage, onDisconnect, onError]);

    const sendMessage = useCallback((message: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    useEffect(() => {
        if (!url) return;

        shouldConnectRef.current = true;
        
        // Small delay to ensure component is fully mounted
        const timer = setTimeout(() => {
            if (shouldConnectRef.current) {
                connect();
            }
        }, 100);
        
        return () => {
            clearTimeout(timer);
            shouldConnectRef.current = false;
            disconnect();
        };
    }, [url]); // Only depend on url, not connect/disconnect

    return {
        isConnected,
        sendMessage,
        disconnect,
        reconnectAttempt,
    };
}