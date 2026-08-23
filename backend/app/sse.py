"""SSE Broadcast Manager - streams real-time alerts to connected clients"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Set
from fastapi import Request


class AlertBroadcaster:
    """Manages SSE connections and broadcasts new alerts to all connected clients in an org."""

    def __init__(self):
        # org_id -> set of asyncio.Queue per client
        self._connections: Dict[int, Set[asyncio.Queue]] = {}

    def subscribe(self, org_id: int) -> asyncio.Queue:
        """Subscribe to alerts for an organization. Returns a Queue to read from."""
        queue: asyncio.Queue = asyncio.Queue()
        if org_id not in self._connections:
            self._connections[org_id] = set()
        self._connections[org_id].add(queue)
        return queue

    def unsubscribe(self, org_id: int, queue: asyncio.Queue):
        """Remove a client subscription."""
        if org_id in self._connections:
            self._connections[org_id].discard(queue)
            if not self._connections[org_id]:
                del self._connections[org_id]

    def broadcast(self, org_id: int, event_type: str, data: dict):
        """Broadcast an event to all connected clients in an organization."""
        if org_id not in self._connections:
            return

        message = {
            "event": event_type,
            "data": json.dumps(data, default=str),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        dead_queues = []
        for queue in self._connections[org_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                dead_queues.append(queue)

        for q in dead_queues:
            self._connections[org_id].discard(q)

    def broadcast_alert(self, org_id: int, alert_data: dict):
        """Convenience: broadcast a new alert event."""
        self.broadcast(org_id, "new_alert", alert_data)

    def broadcast_notification(self, org_id: int, notification_data: dict):
        """Convenience: broadcast a new notification."""
        self.broadcast(org_id, "new_notification", notification_data)

    def get_connected_count(self, org_id: int) -> int:
        """Get number of connected clients for an org."""
        return len(self._connections.get(org_id, set()))


# Global singleton
alert_broadcaster = AlertBroadcaster()
