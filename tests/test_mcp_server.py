"""Unit tests for Em-Cubed Model Context Protocol (MCP) Gateway Server."""

from em_cubed.gateway.mcp_server import EmCubedMCPServer


def test_mcp_server_tools_list():
    server = EmCubedMCPServer()
    assert len(server.TOOLS) == 11
    tool_names = [t["name"] for t in server.TOOLS]
    assert "em_cubed_validate_triple" in tool_names
    assert "em_cubed_elicit_ontology" in tool_names
    assert "em_cubed_evaluate_topos" in tool_names
    assert "em_cubed_extract_truthmakers" in tool_names
    assert "em_cubed_prove_zkp" in tool_names
    assert "em_cubed_check_health" in tool_names
    assert "em_cubed_run_monad" in tool_names
    assert "em_cubed_run_geopolitical_sim" in tool_names
    assert "em_cubed_search_skills" in tool_names
    assert "em_cubed_list_surfaces" in tool_names
    assert "em_cubed_execute_skill" in tool_names


def test_mcp_call_list_surfaces():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_list_surfaces", {})
    assert "surfaces" in res
    surface_names = [s["name"] for s in res["surfaces"]]
    assert "python" in surface_names
    assert "prolog" in surface_names
    assert "z3" in surface_names


def test_mcp_call_search_skills():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_search_skills", {"query": "python"})
    assert "skills" in res
    assert isinstance(res["skills"], list)



def test_mcp_call_validate_triple():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_validate_triple", {"subject": "Agent_X", "predicate": "hasRole", "object": "Auditor"})
    assert res["valid"] is True


def test_mcp_call_evaluate_topos():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_evaluate_topos", {"confidence": 0.95})
    assert res["satisfied"] is True
    assert res["modal_type"] == "Necessary"


def test_mcp_call_extract_truthmakers():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_extract_truthmakers", {"proposition": "Security Audit", "subject": "Node_A", "object": "Cluster_B"})
    assert res["proposition"] == "Security Audit"


def test_mcp_call_prove_zkp():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_prove_zkp", {"proposition": "ZKP Compliance", "subject": "Node_A", "object": "Cluster_B"})
    assert "proof_id" in res
    assert "merkle_state_root" in res


def test_mcp_call_check_health():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_check_health", {})
    assert "coherence_index" in res
    assert res["health_status"] == "HEALTHY"


def test_mcp_call_run_monad():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_run_monad", {"subject": "Agent_X", "predicate": "hasRole", "object": "Auditor"})
    assert "(check-sat)" in res["smt_lib"]


def test_mcp_call_run_geopolitical_sim():
    server = EmCubedMCPServer()
    res = server.call_tool("em_cubed_run_geopolitical_sim", {"scenario": "default", "steps": 5})
    assert res["status"] == "COMPLETED"
    assert res["topos_omega_status"] == "NECESSARY"
