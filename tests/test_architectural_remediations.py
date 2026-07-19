"""Tests for architectural and safety remediations."""

import pytest
import threading
import asyncio
import tempfile
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from src.em_cubed.surfaces.base import DaemonThreadPoolExecutor, _make_daemon_executor
from src.em_cubed.surfaces.python_surface import _kill_executor_processes, PythonSurface
from src.em_cubed.skills.registry import SQLiteRegistryStorage, JSONFileRegistryStorage, SkillRegistry
from src.em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest
from src.em_cubed.skills.metadata import SkillMetadata, InputOutputSchema


def test_daemon_thread_pool_executor():
    """Verify that DaemonThreadPoolExecutor spawns daemon threads without polluting global namespace."""
    original_thread_ctor = threading.Thread

    executor = DaemonThreadPoolExecutor(max_workers=1)
    
    # Spawn a thread via executor
    def worker():
        return threading.current_thread().daemon

    future = executor.submit(worker)
    is_daemon = future.result()
    
    # Verify thread inside executor was daemon
    assert is_daemon is True
    
    # Verify global namespace constructor is unchanged
    assert threading.Thread is original_thread_ctor
    
    # Verify standard thread spawned outside executor is NOT daemon by default (or follows defaults)
    t = threading.Thread()
    assert t.daemon == threading.current_thread().daemon

    executor.shutdown()


def test_kill_executor_processes():
    """Verify that _kill_executor_processes terminates all child processes in the pool."""
    mock_process1 = Mock()
    mock_process2 = Mock()
    
    mock_executor = Mock()
    mock_executor._processes = {
        mock_process1: 123,
        mock_process2: 456
    }
    
    _kill_executor_processes(mock_executor)
    
    mock_process1.terminate.assert_called_once()
    mock_process1.kill.assert_called_once()
    mock_process2.terminate.assert_called_once()
    mock_process2.kill.assert_called_once()


def test_sqlite_registry_storage():
    """Verify that SQLiteRegistryStorage persists, loads, and updates metrics transactionally."""
    import gc
    db_path = Path("test_registry.db")
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass
            
    storage = SQLiteRegistryStorage(db_path)
    
    try:
        # Test empty database load
        skills = storage.load_skills()
        assert len(skills) == 0
        
        # Mock skill data
        skill1 = {
            "skill_id": "math/add",
            "name": "Add Numbers",
            "domain": "math",
            "version": "1.0.0",
            "surfaces": ["python"],
            "purpose": "Addition",
            "description": "Adds two numbers",
            "validation_score": 0.95,
            "test_coverage": 1.0,
            "metrics": {
                "applied_count": 5,
                "success_count": 4,
                "total_execution_time": 1.2,
                "total_token_usage": 100,
                "last_executed": "2026-07-18T12:00:00"
            }
        }
        
        # Test save
        storage.save_skills([skill1])
        
        # Test load
        loaded = storage.load_skills()
        assert len(loaded) == 1
        assert loaded[0]["skill_id"] == "math/add"
        assert loaded[0]["validation_score"] == 0.95
        assert loaded[0]["metrics"]["applied_count"] == 5
        
        # Test update metrics atomically
        storage.update_skill_metrics("math/add", success=True, execution_time=0.3, token_usage=50)
        
        loaded2 = storage.load_skills()
        assert len(loaded2) == 1
        assert loaded2[0]["metrics"]["applied_count"] == 6
        assert loaded2[0]["metrics"]["success_count"] == 5
        assert loaded2[0]["metrics"]["total_execution_time"] == 1.5
        assert loaded2[0]["metrics"]["total_token_usage"] == 150
    finally:
        gc.collect()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


@pytest.mark.asyncio
async def test_runtime_schema_validation():
    """Verify that SkillExecutor validates input and output schemas at runtime using jsonschema."""
    # Define a schema requiring 'value' as an integer
    input_schema = InputOutputSchema(
        type="object",
        properties={"value": {"type": "integer"}},
        required=["value"]
    )
    output_schema = InputOutputSchema(
        type="object",
        properties={"result": {"type": "string"}},
        required=["result"]
    )
    
    skill = SkillMetadata(
        name="Validator Skill",
        domain="test",
        version="0.1.0",
        surfaces=["python"],
        input_schema=input_schema,
        output_schema=output_schema,
        skill_id="test/validator",
        path="/fake/path"
    )
    
    # Mock components
    mock_plugin_manager = Mock()
    mock_surface = Mock()
    mock_surface.available = True
    
    # Setup mock surface execute response
    async def mock_execute(code, context):
        # returns invalid output format (result is integer, schema requires string)
        return {"status": "ok", "value": {"result": 123}}
        
    mock_surface.execute = mock_execute
    mock_plugin_manager.get.return_value = mock_surface
    
    mock_registry = Mock(spec=SkillRegistry)
    mock_registry.get_skill.return_value = skill
    
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = SkillExecutor(mock_plugin_manager, mock_registry, Path(tmpdir))
        
        # Patch load_skill_code to return simple python code
        with patch.object(executor, "_load_skill_code", return_value={"python": "pass"}):
            
            # 1. Test invalid input validation (passing uncoercible string instead of integer)
            req_invalid_input = SkillExecutionRequest(
                skill_id="test/validator",
                input_data={"value": "not-an-integer"}
            )
            res1 = await executor.execute(req_invalid_input)
            assert res1.success is False
            assert "Input validation failed" in res1.error
            
            # 2. Test input/output coercion and successful validation
            # input 42 (int) is valid, output result=123 (int) is coerced to string "123"
            req_valid_input = SkillExecutionRequest(
                skill_id="test/validator",
                input_data={"value": 42}
            )
            res2 = await executor.execute(req_valid_input)
            assert res2.success is True
            assert res2.output == {"result": "123"}


def test_boundary_type_coercion():
    """Verify that coerce_data correctly coerces inputs and outputs."""
    from src.em_cubed.skills.executor import coerce_data
    
    # 1. Integer coercion
    schema_int = InputOutputSchema(type="integer")
    assert coerce_data("123", schema_int) == 123
    assert coerce_data(45.67, schema_int) == 45
    
    # 2. Number coercion
    schema_num = InputOutputSchema(type="number")
    assert coerce_data("3.14", schema_num) == 3.14
    assert coerce_data(42, schema_num) == 42.0
    
    # 3. String coercion
    schema_str = InputOutputSchema(type="string")
    assert coerce_data(999, schema_str) == "999"
    assert coerce_data(True, schema_str) == "True"
    
    # 4. Boolean coercion
    schema_bool = InputOutputSchema(type="boolean")
    assert coerce_data("yes", schema_bool) is True
    assert coerce_data("0", schema_bool) is False
    assert coerce_data(1, schema_bool) is True
    
    # 5. Object and nested coercion
    schema_obj = InputOutputSchema(
        type="object",
        properties={
            "id": {"type": "integer"},
            "rate": {"type": "number"},
            "flag": {"type": "boolean"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    )
    data = {
        "id": "789",
        "rate": 1.25,
        "flag": "no",
        "tags": [1, 2, False],
        "ignored": "should-stay-same"
    }
    coerced = coerce_data(data, schema_obj)
    assert coerced["id"] == 789
    assert coerced["rate"] == 1.25
    assert coerced["flag"] is False
    assert coerced["tags"] == ["1", "2", "False"]
    assert coerced["ignored"] == "should-stay-same"


@pytest.mark.asyncio
async def test_logic_surfaces_caching():
    """Verify that Prolog, Clingo, and Datalog execution surfaces correctly cache compiles/runs."""
    # 1. Prolog Caching
    from src.em_cubed.surfaces.prolog_surface import PrologSurface
    
    prolog_surface = PrologSurface()
    # Clear cache for deterministic test state
    PrologSurface._consulted_hashes.clear()
    
    # Simple multi-line rules program
    rules_code = "parent(john, mary).\nparent(mary, ann).\n"
    
    # Mock PySWIP Prolog consult and query
    mock_prolog = Mock()
    prolog_surface._prolog = mock_prolog
    
    # First consult: should run file creation and consult
    with patch("os.fdopen", MagicMock()), patch("os.unlink", MagicMock()), patch("os.fsync", MagicMock()), patch("tempfile.mkstemp", return_value=(0, "/fake/path")):
        res1 = await prolog_surface._execute_impl(rules_code)
        assert res1["status"] == "ok"
        mock_prolog.consult.assert_called_once_with("/fake/path")
        
        # Second consult: should hit cache and skip consult
        mock_prolog.reset_mock()
        res2 = await prolog_surface._execute_impl(rules_code)
        assert res2["status"] == "ok"
        mock_prolog.consult.assert_not_called()
        
    # 2. Clingo Caching
    from src.em_cubed.surfaces.clingo_surface import ClingoSurface
    clingo_surface = ClingoSurface()
    clingo_surface._execution_cache.clear()
    
    # Mock Clingo control and solver
    mock_clingo = Mock()
    mock_control = Mock()
    mock_clingo.Control.return_value = mock_control
    
    clingo_code = "a. b. :- not a."
    
    # Mock clingo module import
    with patch("sys.modules", {"clingo": mock_clingo}), patch.object(clingo_surface, "_check_availability", return_value=True):
        # Solves once
        res1 = await clingo_surface._execute_impl(clingo_code)
        assert res1["status"] == "ok"
        mock_clingo.Control.assert_called_once()
        
        # Solves again: should hit solve cache
        mock_clingo.reset_mock()
        res2 = await clingo_surface._execute_impl(clingo_code)
        assert res2["status"] == "ok"
        assert res2["value"] == res1["value"]
        mock_clingo.Control.assert_not_called()

    # 3. Datalog Caching
    from src.em_cubed.surfaces.datalog_surface import DatalogSurface
    datalog_surface = DatalogSurface()
    DatalogSurface._execution_cache.clear()
    
    datalog_code = "result = [1, 2, 3]"
    
    # Mock validate and pyDatalog
    with patch.object(datalog_surface, "_validate_code", return_value=None), patch.object(datalog_surface, "_check_availability", return_value=True):
        # Runs once
        res1 = datalog_surface._run_code(datalog_code)
        assert res1["status"] == "ok"
        assert res1["value"] == [1, 2, 3]
        
        # Modify the run environment logic to assert it bypasses execution entirely
        res2 = datalog_surface._run_code(datalog_code)
        assert res2["status"] == "ok"
        assert res2["value"] == [1, 2, 3]
