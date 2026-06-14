"""Integration tests for assert_context_gate stochastic process skill."""


def build_context_facts(agent_state: dict) -> list:
    facts = []
    if "capability" in agent_state:
        facts.append(
            f"capability_permits({agent_state['capability']}, CURRENT_ACTION)."
        )
    if "resource_level" in agent_state:
        facts.append(f"resource_context({agent_state['resource_level']}).")
    if "recent_transitions" in agent_state:
        for f, t in agent_state["recent_transitions"][-5:]:
            facts.append(f"recent_transition({f}, {t}).")
    if agent_state.get("safe_targets"):
        for t in agent_state["safe_targets"]:
            facts.append(f"safe_target({t}).")
    return facts


_CAPABILITY_TABLE = {
    ("nlp_predict", "generate_token"),
    ("nlp_predict", "end_sequence"),
    ("walk", "follow_link"),
    ("walk", "teleport"),
    ("optimize", "take_step"),
}

_COSTS = {
    "follow_link": 1,
    "teleport": 3,
    "generate_token": 1,
    "take_step": 5,
}


def capability_permits(cap: str, action: str) -> bool:
    return (cap, action) in _CAPABILITY_TABLE


def resource_sufficient(level: int, action: str) -> bool:
    cost = _COSTS.get(action, 1)
    return level >= cost


def recently_visited(from_, to_, history: list) -> bool:
    recent = history[-3:]
    return (from_, to_) in recent


_SAFE_TARGETS = {"home", "park", "cafe", "office"}


def safe_target(target: str, unsafe_set: set) -> bool:
    return target not in unsafe_set


def evaluate_gate(from_, to_, agent_state) -> tuple:
    capability = agent_state.get("capability", "")
    resource = agent_state.get("resource_level", 0)
    history = agent_state.get("recent_transitions", [])
    action = to_

    cap_ok = capability_permits(capability, action)
    res_ok = resource_sufficient(resource, action)
    rec_ok = not recently_visited(from_, to_, history)

    if "safe_targets" in agent_state and agent_state["safe_targets"]:
        safe_ok = to_ in agent_state["safe_targets"]
    else:
        unsafe = set(agent_state.get("unsafe_targets", ["dead_end", "void"]))
        safe_ok = safe_target(to_, unsafe)

    blocks = []
    if not cap_ok:
        blocks.append("no_capability")
    if not res_ok:
        blocks.append("insufficient_resource")
    if not rec_ok:
        blocks.append("recent_loop")
    if not safe_ok:
        blocks.append("unsafe_target")

    allowed = cap_ok and res_ok and rec_ok and safe_ok
    return allowed, tuple(blocks)


class TestBuildContextFacts:
    def test_capability_only(self):
        facts = build_context_facts({"capability": "walk"})
        assert "capability_permits(walk, CURRENT_ACTION)." in facts
        assert len(facts) == 1

    def test_resource_only(self):
        facts = build_context_facts({"resource_level": 10})
        assert "resource_context(10)." in facts
        assert len(facts) == 1

    def test_recent_transitions(self):
        state = {"recent_transitions": [("a", "b"), ("c", "d")]}
        facts = build_context_facts(state)
        assert "recent_transition(a, b)." in facts
        assert "recent_transition(c, d)." in facts
        assert len(facts) == 2

    def test_recent_transitions_truncated_to_last_five(self):
        state = {"recent_transitions": [(chr(97 + i), chr(97 + i + 1)) for i in range(7)]}
        facts = build_context_facts(state)
        assert len(facts) == 5

    def test_safe_targets(self):
        facts = build_context_facts({"safe_targets": ["home", "park"]})
        assert "safe_target(home)." in facts
        assert "safe_target(park)." in facts
        assert len(facts) == 2

    def test_empty_safe_targets(self):
        facts = build_context_facts({"safe_targets": []})
        assert facts == []

    def test_safe_targets_none(self):
        facts = build_context_facts({"safe_targets": None})
        assert facts == []

    def test_all_combined(self):
        state = {
            "capability": "walk",
            "resource_level": 5,
            "recent_transitions": [("x", "y")],
            "safe_targets": ["home"],
        }
        facts = build_context_facts(state)
        assert len(facts) == 4
        assert any("capability_permits" in f for f in facts)
        assert any("resource_context" in f for f in facts)
        assert any("recent_transition" in f for f in facts)
        assert any("safe_target" in f for f in facts)


class TestCapabilityPermits:
    def test_known_action_allowed(self):
        assert capability_permits("nlp_predict", "generate_token") is True

    def test_walk_follow_link_allowed(self):
        assert capability_permits("walk", "follow_link") is True

    def test_walk_teleport_allowed(self):
        assert capability_permits("walk", "teleport") is True

    def test_optimize_take_step_allowed(self):
        assert capability_permits("optimize", "take_step") is True

    def test_unknown_blocked(self):
        assert capability_permits("walk", "fly") is False

    def test_unknown_capability_blocked(self):
        assert capability_permits("hacker", "break_system") is False


class TestResourceSufficient:
    def test_sufficient_resource(self):
        assert resource_sufficient(5, "follow_link") is True

    def test_insufficient_blocked(self):
        assert resource_sufficient(0, "follow_link") is False

    def test_move_costs_more_than_default(self):
        assert resource_sufficient(2, "teleport") is False
        assert resource_sufficient(3, "teleport") is True

    def test_take_step_high_cost(self):
        assert resource_sufficient(4, "take_step") is False
        assert resource_sufficient(5, "take_step") is True

    def test_unknown_action_cost_defaults_to_one(self):
        assert resource_sufficient(1, "unknown") is True
        assert resource_sufficient(0, "unknown") is False


class TestRecentlyVisited:
    def test_not_in_history_passes(self):
        history = [("a", "b"), ("c", "d"), ("e", "f")]
        assert recently_visited("a", "c", history) is False

    def test_in_recent_history_blocked(self):
        history = [("a", "b"), ("c", "d"), ("e", "f")]
        assert recently_visited("c", "d", history) is True

    def test_empty_history_passes(self):
        assert recently_visited("a", "b", []) is False

    def test_history_longer_than_three_uses_only_last_three(self):
        history = [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")]
        assert recently_visited("g", "h", history) is True


class TestSafeTarget:
    def setup_method(self):
        self.unsafe = {"dead_end", "void"}

    def test_safe_target(self):
        assert safe_target("home", self.unsafe) is True

    def test_dead_end_blocked(self):
        assert safe_target("dead_end", self.unsafe) is False

    def test_void_blocked(self):
        assert safe_target("void", self.unsafe) is False

    def test_empty_unsafe_set_passes_all(self):
        assert safe_target("anything", set()) is True


class TestEvaluateGate:
    def test_all_gates_pass(self):
        state = {
            "capability": "walk",
            "resource_level": 10,
            "recent_transitions": [],
            "unsafe_targets": [],
        }
        allowed, blocks = evaluate_gate("a", "follow_link", state)
        assert allowed is True
        assert blocks == ()

    def test_capability_blocked(self):
        state = {
            "capability": "hacker",
            "resource_level": 10,
            "recent_transitions": [],
            "unsafe_targets": [],
        }
        allowed, blocks = evaluate_gate("a", "follow_link", state)
        assert allowed is False
        assert "no_capability" in blocks

    def test_resource_blocked(self):
        state = {
            "capability": "walk",
            "resource_level": 0,
            "recent_transitions": [],
            "unsafe_targets": [],
        }
        allowed, blocks = evaluate_gate("a", "follow_link", state)
        assert allowed is False
        assert "insufficient_resource" in blocks

    def test_recency_blocked(self):
        state = {
            "capability": "walk",
            "resource_level": 10,
            "recent_transitions": [("a", "follow_link")],
            "unsafe_targets": [],
        }
        allowed, blocks = evaluate_gate("a", "follow_link", state)
        assert allowed is False
        assert "recent_loop" in blocks

    def test_safety_blocked(self):
        state = {
            "capability": "walk",
            "resource_level": 10,
            "recent_transitions": [],
            "unsafe_targets": ["dead_end"],
        }
        allowed, blocks = evaluate_gate("a", "dead_end", state)
        assert allowed is False
        assert "unsafe_target" in blocks

    def test_multiple_blocks_reported(self):
        state = {
            "capability": "hacker",
            "resource_level": 0,
            "recent_transitions": [("a", "dead_end")],
            "unsafe_targets": ["dead_end"],
        }
        allowed, blocks = evaluate_gate("a", "dead_end", state)
        assert allowed is False
        assert len(set(blocks)) == 4
