# Neuro-Symbolic Ontology & Loopy Skill Framework Guide

The **Em-Cubed Loopy Skill & Ontology Framework** bridges probabilistic AI models with deterministic symbolic logic. It implements the core architecture from *"Why Agentic Systems Need Ontologies"* (Frank Coyle) and *"Loop Engineering: Beyond the Hype"*.

---

## Key Architectural Concepts

### 1. "Pydantic at the Door, Ontology at the Ledger"
- **Door Validation (Pydantic)**: Ensures incoming payloads match expected data types and structural formats before entering an operational loop.
- **Ledger Validation (Ontology)**: Uses formal semantic constraints (functional uniqueness, class disjointness, domain/range inferences) to verify business logic rules before committing state transitions to the database or knowledge graph.

### 2. Loopy Skills (Iterative Sub-Routines)
Traditional tools are linear (`tool(args) -> Result`). A **Loopy Skill** is a stateful, iterative sub-routine (`loopy_tool(goal, max_iter, criteria) -> LoopResult`) that manages its own retries, local memory, and verification sensors.

---

## Subsystem Overview

```
em_cubed/
├── loopy/
│   ├── base.py       # BaseLoopySkill, LoopTrajectory, LoopySkillResult
│   ├── runner.py     # LoopySkillRunner scope controller
│   └── miner.py      # TextLoopMiner (Procedural SOP text -> MinedLoopSchema)
└── ontology/
    ├── schema.py     # OntologyTriple, FunctionalPropertyConstraint, DisjointClassConstraint
    └── validator.py  # OntologyLedgerValidator
```

---

## Real-World Use Cases & Practical Examples

### Use Case 1: Self-Correcting Code Refactoring Loop

**Problem**: Main agent context windows get bloated by logging 10 retries of linter errors during code generation.  
**Solution**: Offload the edit-and-test cycle into an isolated `BaseLoopySkill`.

```python
from dataclasses import dataclass, field
from em_cubed.loopy import BaseLoopySkill, LoopySkillRunner

@dataclass
class CodeState:
    file_path: str
    code_content: str
    linter_errors: list[str] = field(default_factory=list)

class AutoRefactorSkill(BaseLoopySkill[CodeState, str]):
    def initialize_state(self, file_path: str, initial_code: str) -> CodeState:
        return CodeState(
            file_path=file_path,
            code_content=initial_code,
            linter_errors=["E501 line too long", "F401 unused import"]
        )

    def mutate(self, state: CodeState, iteration: int) -> tuple[CodeState, str]:
        if state.linter_errors:
            fixed_err = state.linter_errors.pop(0)
            state.code_content += f"\n# Fixed: {fixed_err}"
            action = f"Applied patch for {fixed_err}"
        else:
            action = "No pending errors"
        return state, action

    def verify(self, state: CodeState) -> tuple[bool, str]:
        # Deterministic Guardrail Sensor
        if not state.linter_errors:
            return True, "Linter passed (0 errors)"
        return False, f"Linter failed: {len(state.linter_errors)} remaining errors"

    def extract_result(self, state: CodeState) -> str:
        return state.code_content

# Execute Loopy Skill
skill = AutoRefactorSkill(max_iterations=5)
result = LoopySkillRunner.execute(skill, file_path="src/utils.py", initial_code="def main(): pass")

print(f"Success: {result.success}")
print(f"Iterations Taken: {len(result.trajectory)}")
for step in result.trajectory:
    print(f" Iteration {step.iteration}: {step.action_taken} -> Guard Passed: {step.passed_guard}")
```

---

### Use Case 2: Financial Payout Ledger with Ontology Guardrails

**Problem**: AI agents executing customer payouts can hallucinate duplicate refunds or confuse support reps with customers.  
**Solution**: Enforce **Functional Property Uniqueness** and **Disjoint Class Constraints** at the ledger.

```python
from pydantic import BaseModel, Field
from em_cubed.ontology import OntologyLedgerValidator, OntologyTriple

# 1. Pydantic Door Schema
class PayoutPayload(BaseModel):
    order_id: str = Field(..., min_length=3)
    amount: float = Field(..., gt=0)
    recipient_id: str

# 2. Initialize Ontology Ledger Validator
validator = OntologyLedgerValidator()

# Enforce: An order can have at most ONE refund issued (Functional Property)
validator.add_functional_property("has_refund")

# Enforce: An entity cannot be both a Customer and a SupportRep (Disjoint Classes)
validator.add_disjoint_classes("Customer", "SupportRep")
validator.add_domain_range_inference("issues_payout_to", domain_class="FinanceEngine", range_class="Customer")
validator.add_domain_range_inference("assigns_ticket_to", domain_class="Helpdesk", range_class="SupportRep")

# --- Example Execution ---
valid_payload = {"order_id": "ORD-99", "amount": 149.99, "recipient_id": "USER_01"}
triple_1 = OntologyTriple(subject="ORD-99", predicate="has_refund", object="REFUND-01")

# Door + Ledger Validation
success, msg = validator.validate_and_commit(
    new_triple=triple_1,
    schema_model=PayoutPayload,
    raw_payload=valid_payload
)
print(f"First Refund: {success} ({msg})")

# Attempt Duplicate Refund (Fails Functional Property Check)
triple_2 = OntologyTriple(subject="ORD-99", predicate="has_refund", object="REFUND-02")
success_2, msg_2 = validator.validate_and_commit(new_triple=triple_2)
print(f"Duplicate Refund: {success_2} ({msg_2})")
# Output: Duplicate Refund: False (Functional Property Violation on predicate 'has_refund': ...)
```

---

### Use Case 3: Mining Executable Loops from SOP Runbooks

**Problem**: Technical runbooks and legal policies contain implicit procedures that aren't formal software loops.  
**Solution**: Use `TextLoopMiner` to convert raw documentation into structured `MinedLoopSchema` targets.

```python
from em_cubed.loopy import TextLoopMiner

sop_document = """
STANDARD OPERATING PROCEDURE: Server Patching
WHEN a critical vulnerability alert triggers for web servers
DO apply security patch and restart application service
UNTIL verify health check HTTP 200 OK and zero active alarms
"""

miner = TextLoopMiner()
mined_loops = miner.mine_loops_from_text(sop_document, default_name="ServerPatchingLoop")

for loop in mined_loops:
    print(f"Loop Name: {loop.name}")
    print(f"Trigger:   {loop.trigger}")
    print(f"Actions:   {loop.action_sequence}")
    print(f"Exit Cond: {loop.exit_condition}")
    print(f"Max Retries: {loop.max_retries}")
```

---

## Best Practices & Recommendations

1. **Keep Guardrails Deterministic**: Use subprocess linter runs, AST verifiers, or ontology constraint checkers for `verify()`, rather than asking an LLM to evaluate itself.
2. **Isolate Scope**: Keep intermediate retry attempts inside the loopy skill's trajectory to maintain context window sanity in outer agent orchestrators.
3. **Ontology at the Ledger**: Never write to primary databases until the `OntologyLedgerValidator` approves functional property, disjointness, and domain/range rules.
