"""Telemetry API for real-time observability dashboard."""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import structlog

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
        return self.collector.get_skill_metrics(skill_id, window_seconds)
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall telemetry statistics."""
        return self.collector.get_overall_stats()
    
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
    
    def subscribe(self, websocket):
        """Subscribe a WebSocket client to telemetry updates."""
        self._subscribers.append(websocket)
        self.logger.info("WebSocket client subscribed", count=len(self._subscribers))
    
    def unsubscribe(self, websocket):
        """Unsubscribe a WebSocket client."""
        if websocket in self._subscribers:
            self._subscribers.remove(websocket)
        self.logger.info("WebSocket client unsubscribed", count=len(self._subscribers))
    
    async def broadcast_telemetry_update(self, data: Dict[str, Any]):
        """Broadcast telemetry update to all subscribers."""
        # In a real implementation, this would send to all WebSocket connections
        self.logger.debug("Broadcasting telemetry update", data_keys=list(data.keys()))
        # Placeholder for actual WebSocket broadcasting
        pass
    
    def record_execution_with_notification(self, record):
        """Record execution and notify subscribers."""
        self.collector.record_execution(record)
        # Notify subscribers of new execution
        # In real implementation: await self.broadcast_telemetry_update({
        #     "type": "execution_record",
        #     "data": record.to_dict()
        # })


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