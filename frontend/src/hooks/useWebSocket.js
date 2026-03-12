import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Hook that connects to the toll dashboard WebSocket.
 * Returns the latest event and a `connected` boolean.
 */
export function useWebSocket() {
  const [lastEvent, setLastEvent] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const connectRef = useRef(null);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${protocol}://${window.location.host}/ws/toll/dashboard/`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log('[WS] Connected to toll dashboard');
    };

    ws.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        setLastEvent(payload);
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('[WS] Disconnected — reconnecting in 3 s');
      reconnectTimer.current = setTimeout(() => connectRef.current(), 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  useEffect(() => {
    connectRef.current();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  return { lastEvent, connected };
}
