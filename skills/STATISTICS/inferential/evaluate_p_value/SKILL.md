---
name: evaluate_p_value
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Hybrid inferential skill translating numerically computed p-values into formal hypothesis testing conclusions (reject_null or fail_to_reject_null) under first-order logic rules in Prolog. Supports two-tailed, left-tailed, and right-tailed critical evaluation against significance threshold alpha with human-readable evidence strings and machine-readable state assertions. Use when concluding statistical hypothesis tests, gating decision pipelines on statistical significance, or constructing formal research reporting.
purpose: Translate numerical p-values into formal logical hypothesis conclusions and structured evidence records.
dependencies: []
tags:
  - p-value
  - hypothesis-testing
  - significance-level
  - alpha-threshold
  - prolog-formalization
inputs:
  p_value:
    type: number
    required: true
    description: Computed test statistic p-value $p \in [0.0, 1.0]$.
  alpha:
    type: number
    required: false
    description: Significance threshold $\alpha \in (0, 1)$ (default 0.05).
  tail:
    type: string
    required: false
    description: Directionality of the hypothesis test ('two', 'left', 'right').
outputs:
  decision:
    type: string
    description: Formal decision atom ('reject_null' or 'fail_to_reject_null').
  state:
    type: string
    description: Machine-readable hypothesis state ('rejected' or 'not_rejected').
  evidence_string:
    type: string
    description: Formatted narrative summary stating alpha, p-value, and inferential conclusion.
---

# Evaluate P Value Engine

`evaluate_p_value` translates empirical test $p$-values into formal statistical decisions using **first-order logic rules in Prolog** combined with **Python formatting**:

$$\text{Decision} = \begin{cases} \text{reject\_null} & p < \alpha \\ \text{fail\_to\_reject\_null} & p \ge \alpha \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage P-Value Evaluation Progression

```
[1. P-Value & Alpha Bound Audit] → [2. Prolog Hypothesis State Routing] → [3. Visual Brief] → [4. Checkpoint] → [5. Formal Evidence String Emit]
```

### Stage 1: P-Value & Alpha Bound Audit
1. Ingest `p_value` ($0.0 \le p \le 1.0$) and `alpha` ($0.0 < \alpha < 1.0$).
2. Validate tail specification (`two`, `left`, `right`).

> **Completion criterion**: Bounded $p \in [0, 1]$ and valid significance threshold $\alpha$ verified.

---

### Stage 2: Prolog Hypothesis State Routing
1. Evaluate core threshold predicate in Prolog:
   ```prolog
   hypothesis_state(P, Alpha, reject_null) :- P < Alpha.
   hypothesis_state(P, Alpha, fail_to_reject_null) :- P >= Alpha.
   ```
2. For one-tailed tests, adjust comparison probability against the directional boundary.

> **Completion criterion**: Formal decision atom and symbolic state mapped.

---

### Stage 3: The Visual Brief
For borderline p-values ($0.04 < p < 0.06$) or critical hypothesis decisions, generate an interactive brief:
- **Location**: Write to `%TEMP%\p-value-brief-<timestamp>.html` (Windows) or `/tmp/p-value-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render null distribution PDF curve, critical rejection region $\alpha$, and test statistic point marker.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing statistical reporting:
1. Check for alpha-boundary equality ($p = \alpha$). Note that $p = \alpha$ strictly fails to reject $H_0$ ($p \not< \alpha$).
2. Record whether test was pre-registered or exploratory to guard against p-hacking interpretation.

> **Completion criterion**: Boundary condition evaluated and recorded in diagnostic payload.

---

### Stage 5: Formal Evidence String Emission
1. Format human-readable narrative string:
   $$\text{"At } \alpha = 0.05\text{, reject the null hypothesis } [p = 0.0024]\text{"}$$
2. Emit complete `PValueResult` record.

> **Completion criterion**: Formally structured result emitted with decision, state, and narrative.

---

## Surface References

### Python Implementation Surface

```python
from typing import Dict, Any

def evaluate_p_value(p_value: float, alpha: float = 0.05, tail: str = "two") -> Dict[str, Any]:
    if not (0.0 <= p_value <= 1.0):
        raise ValueError(f"invalid_p_value: p_value must be in [0, 1], got {p_value}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"invalid_alpha: alpha must be in (0, 1), got {alpha}")
        
    if p_value < alpha:
        decision = "reject_null"
        state = "rejected"
    else:
        decision = "fail_to_reject_null"
        state = "not_rejected"
        
    action_text = "reject" if decision == "reject_null" else "fail to reject"
    evidence_str = f"At α = {alpha}, {action_text} the null hypothesis [p = {p_value:.6f}]."
    
    return {
        "p_value": round(p_value, 6),
        "alpha": alpha,
        "decision": decision,
        "state": state,
        "evidence_string": evidence_str
    }
```

### Prolog Decision Surface

```prolog
valid_alpha(A) :- A > 0, A < 1.

hypothesis_state(P, Alpha, reject_null) :- P < Alpha.
hypothesis_state(P, Alpha, fail_to_reject_null) :- P >= Alpha.

formal_conclusion(reject_null, state(rejected), 'Reject H0').
formal_conclusion(fail_to_reject_null, state(not_rejected), 'Fail to reject H0').
```

---

## Anti-Patterns & Guardrails

- **"Accept the Null Hypothesis" Phrasing** — Stating that $H_0$ is "proven" or "accepted" rather than the mathematically correct "fail to reject $H_0$".
- **Boundary Inclusion Error** — Incorrectly rejecting $H_0$ when $p = \alpha$. Rejection strictly requires $p < \alpha$.
- **Unbounded Alpha Values** — Accepting $\alpha \ge 1.0$ or $\alpha \le 0.0$.
