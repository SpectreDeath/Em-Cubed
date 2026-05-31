"""Telemetry API for real-time observability dashboard."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, cast
import structlog
import asyncio

# These would be imported from a web framework like FastAPI in a real implementation
# For now, we'll define the interface and data structures

logger = structlog.get_logger()


class TelemetryAPI:
    """REST API for accessing telemetry data."""
    
    def __init__(self, telemetry_collector):
        self.collector = telemetry_collector
        self.logger = logger.bind(component="telemetry_api")
    
    def get_skill_metrics(self, skill_id: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Get metrics for a specific skill."""
        return cast(Dict[str, Any], self.collector.get_skill_metrics(skill_id, window_seconds))
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall telemetry statistics."""
        return cast(Dict[str, Any], self.collector.get_overall_stats())
    
    def get_recent_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent skill executions."""
        # Get records from collector
        records = self.collector._records[-limit:] if self.collector._records else []
        return [record.to_dict() for record in records]
    
    def get_skill_executions(self, skill_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get executions for a specific skill."""
        cutoff = datetime.now(timezone.utc).timestamp() - 3600  # Last hour
        relevant = [
            r for r in self.collector._records
            if r.skill_id == skill_id and r.timestamp.timestamp() > cutoff
        ][-limit:] if self.collector._records else []
        return [record.to_dict() for record in relevant]
    
    def get_available_skills(self) -> List[str]:
        """Get list of skills with telemetry data."""
        if not self.collector._records:
            return []
        skill_ids = set(r.skill_id for r in self.collector._records)
        return list(skill_ids)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        stats = self.get_overall_stats()
        return {
            "status": "healthy" if stats.get("total_executions", 0) >= 0 else "unknown",
            "total_executions": stats.get("total_executions", 0),
            "success_rate": stats.get("overall_success_rate", 0),
            "unique_skills": stats.get("unique_skills", 0),
            "total_token_usage": stats.get("total_token_usage", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class WebSocketTelemetryHandler:
    """WebSocket handler for real-time telemetry updates."""
    
    def __init__(self, telemetry_collector):
        self.collector = telemetry_collector
        self.logger = logger.bind(component="websocket_telemetry")
        self._subscribers: List[Any] = []  # Would be WebSocket connections
        self._last_broadcast = time.time()
        self._broadcast_interval = 5.0  # Broadcast every 5 seconds
        self._broadcast_task: Optional[asyncio.Task] = None
    
    def subscribe(self, websocket):
        """Subscribe a WebSocket client to telemetry updates."""
        self._subscribers.append(websocket)
        self.logger.info("WebSocket client subscribed", count=len(self._subscribers))
        # Start broadcast task if not already running
        if self._broadcast_task is None or self._broadcast_task.done():
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())
    
    def unsubscribe(self, websocket):
        """Unsubscribe a WebSocket client."""
        if websocket in self._subscribers:
            self._subscribers.remove(websocket)
        self.logger.info("WebSocket client unsubscribed", count=len(self._subscribers))
        # Stop broadcast task if no subscribers
        if len(self._subscribers) == 0 and self._broadcast_task and not self._broadcast_task.done():
            self._broadcast_task.cancel()
    
    async def _broadcast_loop(self):
        """Background task to periodically broadcast telemetry updates."""
        try:
            while True:
                await asyncio.sleep(self._broadcast_interval)
                if self._subscribers:  # Only broadcast if we have subscribers
                    await self.broadcast_telemetry_update()
        except asyncio.CancelledError:
            self.logger.info("WebSocket broadcast task cancelled")
        except Exception as e:
            self.logger.error("Error in WebSocket broadcast loop", error=str(e))
    
    async def broadcast_telemetry_update(self):
        """Broadcast telemetry update to all subscribers."""
        if not self._subscribers:
            return
            
        # Get current telemetry data
        try:
            overall_stats = self.collector.get_overall_stats()
            available_skills = self.get_available_skills()
            
            # Prepare update data
            update_data = {
                "type": "telemetry_update",
                "data": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "overall_stats": overall_stats,
                    "available_skills": available_skills,
                    "total_executions": overall_stats.get("total_executions", 0),
                    "success_rate": overall_stats.get("overall_success_rate", 0),
                    "unique_skills": overall_stats.get("unique_skills", 0)
                }
            }
            
            # Send to each WebSocket connection
            disconnected = []
            for websocket in self._subscribers[:]:  # Copy list to avoid modification during iteration
                try:
                    await websocket.send_json(update_data)
                except Exception:
                    # Mark for removal if we can't send
                    disconnected.append(websocket)
            
            # Remove disconnected clients
            for ws in disconnected:
                if ws in self._subscribers:
                    self._subscribers.remove(ws)
                        
        except Exception as e:
            self.logger.error("Failed to prepare or send telemetry update", error=str(e))
    
    def record_execution_with_notification(self, record):
        """Record execution and notify subscribers."""
        self.collector.record_execution(record)
        # Notify subscribers of new execution - we'll rely on the periodic broadcast
        # for simplicity, but in a high-frequency scenario we might want to broadcast immediately


# Global instances (would be initialized in main app)
_telemetry_api: Optional[TelemetryAPI] = None
_websocket_handler: Optional[WebSocketTelemetryHandler] = None


def initialize_telemetry_api(collector) -> TelemetryAPI:
    """Initialize the telemetry API."""
    global _telemetry_api
    _telemetry_api = TelemetryAPI(collector)
    logger.info("Telemetry API initialized")
    return _telemetry_api


def get_telemetry_api() -> Optional[TelemetryAPI]:
    """Get the global telemetry API instance."""
    return _telemetry_api


def initialize_websocket_handler(collector) -> WebSocketTelemetryHandler:
    """Initialize the WebSocket telemetry handler."""
    global _websocket_handler
    _websocket_handler = WebSocketTelemetryHandler(collector)
    logger.info("WebSocket telemetry handler initialized")
    return _websocket_handler


def get_websocket_handler() -> Optional[WebSocketTelemetryHandler]:
    """Get the global WebSocket handler instance."""
    return _websocket_handler