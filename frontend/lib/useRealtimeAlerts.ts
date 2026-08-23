"use client";
import { useEffect, useRef, useCallback, useState } from "react";

export interface RealtimeAlert {
  id: number;
  title: string;
  severity: string;
  status: string;
  risk_score: number;
  source_ip: string;
  created_at: string;
  [key: string]: any;
}

export interface RealtimeNotification {
  id: number;
  title: string;
  message: string;
  type: string;
  [key: string]: any;
}

interface UseRealtimeOptions {
  orgId: number;
  onAlert?: (alert: RealtimeAlert) => void;
  onNotification?: (notification: RealtimeNotification) => void;
  onAlertUpdate?: (alert: RealtimeAlert) => void;
}

/**
 * Hook that connects to the SSE event stream and provides real-time
 * alert and notification updates. Auto-reconnects on disconnect.
 */
export function useRealtimeAlerts({
  orgId,
  onAlert,
  onNotification,
  onAlertUpdate,
}: UseRealtimeOptions) {
  const [connected, setConnected] = useState(false);
  const [alerts, setAlerts] = useState<RealtimeAlert[]>([]);
  const [notifications, setNotifications] = useState<RealtimeNotification[]>([]);
  const [alertCount, setAlertCount] = useState(0);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbacksRef = useRef({ onAlert, onNotification, onAlertUpdate });

  // Keep callbacks ref fresh
  useEffect(() => {
    callbacksRef.current = { onAlert, onNotification, onAlertUpdate };
  }, [onAlert, onNotification, onAlertUpdate]);

  const connect = useCallback(() => {
    if (!orgId || eventSourceRef.current) return;

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const url = `${backendUrl}/api/events/stream?org_id=${orgId}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener("connected", () => {
      setConnected(true);
    });

    es.addEventListener("new_alert", (event) => {
      try {
        const alert: RealtimeAlert = JSON.parse(event.data);
        setAlerts((prev) => [alert, ...prev].slice(0, 100)); // keep last 100
        setAlertCount((prev) => prev + 1);
        callbacksRef.current.onAlert?.(alert);
      } catch (e) {
        console.error("Failed to parse alert event:", e);
      }
    });

    es.addEventListener("alert_updated", (event) => {
      try {
        const alert: RealtimeAlert = JSON.parse(event.data);
        setAlerts((prev) =>
          prev.map((a) => (a.id === alert.id ? { ...a, ...alert } : a))
        );
        callbacksRef.current.onAlertUpdate?.(alert);
      } catch (e) {
        console.error("Failed to parse alert update:", e);
      }
    });

    es.addEventListener("new_notification", (event) => {
      try {
        const notif: RealtimeNotification = JSON.parse(event.data);
        setNotifications((prev) => [notif, ...prev].slice(0, 50));
        callbacksRef.current.onNotification?.(notif);
      } catch (e) {
        console.error("Failed to parse notification event:", e);
      }
    });

    es.onerror = () => {
      setConnected(false);
      es.close();
      eventSourceRef.current = null;

      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };
  }, [orgId]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [connect]);

  const clearAlertCount = useCallback(() => {
    setAlertCount(0);
  }, []);

  return {
    connected,
    alerts,
    notifications,
    alertCount,
    clearAlertCount,
  };
}
