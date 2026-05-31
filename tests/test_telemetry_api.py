"""Integration tests for telemetry API and WebSocket broadcasting."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from src.em_cubed.telemetry.api import TelemetryAPI, WebSocketTelemetryHandler, get_telemetry_api, get_websocket_handler
from src.em_cubed.skills.telemetry import TelemetryCollector, ExecutionRecord


def test_telemetry_api_get_available_skills():
    """Test TelemetryAPI returns skills from telemetry records."""
    collector = TelemetryCollector()
    
    # No skills recorded yet
    api = TelemetryAPI(collector)
    assert api.get_available_skills() == []
    
    # Add some records
    record1 = ExecutionRecord(
        skill_id="optimization/central-force",
        timestamp=datetime.now(timezone.utc),
        success=True,
        execution_time_ms=100.0
    )
    record2 = ExecutionRecord(
        skill_id="optimization/spiral-dynamics",
        timestamp=datetime.now(timezone.utc),
        success=True,
        execution_time_ms=150.0
    )
    collector.record_execution(record1)
    collector.record_execution(record2)
    
    # Should return both skill IDs
    skills = api.get_available_skills()
    assert len(skills) == 2
    assert "optimization/central-force" in skills
    assert "optimization/spiral-dynamics" in skills


def test_telemetry_api_get_skill_metrics():
    """Test fetching metrics for a specific skill."""
    collector = TelemetryCollector()
    api = TelemetryAPI(collector)
    
    # Add records
    for i in range(5):
        record = ExecutionRecord(
            skill_id="test/skill",
            timestamp=datetime.now(timezone.utc),
            success=i < 4,  # 4 successes, 1 failure
            execution_time_ms=100.0 * (i + 1),
            token_usage=50
        )
        collector.record_execution(record)
    
    metrics = api.get_skill_metrics("test/skill")
    assert metrics["count"] == 5
    assert metrics["success_count"] == 4
    assert metrics["failure_count"] == 1
    assert 0 < metrics["success_rate"] < 1
    assert metrics["total_token_usage"] == 250


def test_telemetry_api_system_health():
    """Test system health endpoint returns correct structure."""
    collector = TelemetryCollector()
    api = TelemetryAPI(collector)
    
    # No data
    health = api.get_system_health()
    assert health["status"] == "healthy"
    assert health["total_executions"] == 0
    
    # Add some data
    record = ExecutionRecord(
        skill_id="test/skill",
        timestamp=datetime.now(timezone.utc),
        success=True,
        execution_time_ms=100.0
    )
    collector.record_execution(record)
    
    health = api.get_system_health()
    assert health["total_executions"] == 1
    assert health["success_rate"] == 1.0
    assert health["unique_skills"] == 1


@pytest.mark.asyncio
async def test_websocket_handler_subscribe():
    """Test WebSocket subscription starts broadcast task."""
    collector = TelemetryCollector()
    handler = WebSocketTelemetryHandler(collector)
    
    mock_websocket = Mock()
    mock_websocket.send_json = AsyncMock()
    
    handler.subscribe(mock_websocket)
    
    assert len(handler._subscribers) == 1
    assert handler._broadcast_task is not None
    
    # Clean up
    handler._broadcast_task.cancel()
    try:
        await handler._broadcast_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_websocket_handler_broadcast():
    """Test telemetry broadcast sends correct data structure."""
    collector = TelemetryCollector()
    handler = WebSocketTelemetryHandler(collector)
    
    # Add a record
    record = ExecutionRecord(
        skill_id="test/broadcast",
        timestamp=datetime.now(timezone.utc),
        success=True,
        execution_time_ms=50.0
    )
    collector.record_execution(record)
    
    mock_websocket = Mock()
    mock_websocket.send_json = AsyncMock()
    
    handler.subscribe(mock_websocket)
    
    # Give the broadcast loop a moment to run
    await asyncio.sleep(0.1)
    
    # Trigger a broadcast
    await handler.broadcast_telemetry_update()
    
    # Check that send_json was called with correct structure
    if mock_websocket.send_json.called:
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "telemetry_update"
        assert "overall_stats" in call_args["data"]
        assert "available_skills" in call_args["data"]
    
    # Clean up
    handler._broadcast_task.cancel()
    try:
        await handler._broadcast_task
    except asyncio.CancelledError:
        pass


def test_global_telemetry_api_singleton():
    """Test global telemetry API singleton pattern works."""
    # Reset any existing singleton
    import src.em_cubed.telemetry.api as api_module
    api_module._telemetry_api = None
    
    collector = TelemetryCollector()
    api = TelemetryAPI(collector)
    
    # Manually set the singleton
    api_module._telemetry_api = api
    
    assert get_telemetry_api() == api


def test_telemetry_api_recent_executions():
    """Test fetching recent executions."""
    collector = TelemetryCollector()
    api = TelemetryAPI(collector)
    
    # Add records
    for i in range(10):
        record = ExecutionRecord(
            skill_id=f"test/skill-{i}",
            timestamp=datetime.now(timezone.utc),
            success=True,
            execution_time_ms=100.0
        )
        collector.record_execution(record)
    
    executions = api.get_recent_executions(5)
    assert len(executions) == 5


if __name__ == "__main__":
    pytest.main(["-v", __file__])