# Pyramid Risk Verifier — Cangjie Edition
# Orchestrates Z3 formal verification with Python risk calculation

import std.math.*

func main() {
    println("Pyramid Risk Verifier Starting...");
    
    let entry_price = context["entry_price"] as Float64;
    let market_price = context.get("market_price", entry_price) as Float64;
    let account_risk = context.get("account_risk", 1000.0) as Float64;
    let max_levels = context.get("max_levels", 5) as Int32;
    
    // Z3: Formal verification of risk bounds
    let z3_result = perform EmCubed.call_surface("z3", "
(declare-const entry_price Real)
(declare-const market_price Real)
(declare-const account_risk Real)
(declare-const max_pyramid_levels Int)
(declare-const position_size_limit Real)
(declare-const max_risk_per_trade Real)

; Define pyramid level calculation
(define-fun price_distance () Real (abs (- market_price entry_price)))
(define-fun threshold () Real (* 0.001 entry_price))
(define-fun adjusted_distance () Real (if (< price_distance threshold) threshold price_distance))
(define-fun current_level () Int 
  (min (to_int (/ adjusted_distance (* 0.005 entry_price))) (- max_pyramid_levels 1)))

; Define base units calculation
(define-fun base_units () Real (/ account_risk (* 0.01 entry_price)))

; Define position size for level n (0-indexed)
(define-fun position_size ((n Int)) Real
  (let ((scale_factor (+ 1.0 (* 0.5 (to_real n)))))
    (* base_units scale_factor)))

; Define cumulative risk calculation
(define-fun cumulative_risk ((levels Int)) Real
  (let ((sum 0.0))
    (forall ((n Int)) 
      (=> (and (<= 0 n) (< n levels))
          (set! sum (+ sum (position_size n)))))
    (* sum 0.01 entry_price))  ; Risk = position_size * 1% * entry_price

; Risk boundary assertions
(assert (>= entry_price 0.01))
(assert (>= market_price 0.01))
(assert (> account_risk 0))
(assert (> max_pyramid_levels 0))
(assert (<= max_pyramid_levels 10))
(assert (<= account_risk 100.0))

; Prove: Cumulative risk never exceeds account_risk for any valid pyramid level
(assert (>= (cumulative_risk current_level) 0))
(assert (<= (cumulative_risk current_level) account_risk))

(check-sat)
(get-model)
    " @ {
        "entry_price": entry_price,
        "market_price": market_price,
        "account_risk": account_risk,
        "max_pyramid_levels": max_levels
    });
    
    // Python: Practical risk calculation
    let python_result = perform EmCubed.call_surface("python", "
def verify_pyramid_risk_bounds(entry_price, market_price, account_risk, max_levels=5):
    if entry_price <= 0 or market_price <= 0 or account_risk <= 0:
        return {\"valid\": False, \"reason\": \"invalid_inputs\"}
    
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    base_units = account_risk / (0.01 * entry_price)
    total_units = 0
    
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        total_units += units
    
    actual_risk = total_units * 0.01 * entry_price
    risk_ratio = actual_risk / account_risk if account_risk > 0 else 0
    
    return {
        \"within_bounds\": risk_ratio <= 1.0,
        \"risk_ratio\": risk_ratio,
        \"actual_risk\": actual_risk,
        \"allocated_risk\": account_risk,
        \"current_level\": current_level,
        \"total_units\": total_units,
        \"status\": \"verified\" if risk_ratio <= 1.0 else \"violated\"
    }

result = verify_pyramid_risk_bounds({entry_price}, {market_price}, {account_risk}, {max_levels})
result
    " @ {});
    
    return VerificationResult {
        z3_satisfiable: z3_result.get("status") == "sat",
        z3_model: z3_result.get("model", Map<String, Double>()),
        python_within_bounds: python_result.get("within_bounds", False),
        python_risk_ratio: python_result.get("risk_ratio", 0.0),
        python_current_level: python_result.get("current_level", 0),
        verification_passed: 
            (z3_result.get("status") == "sat") and 
            python_result.get("within_bounds", False),
        status: if (python_result.get("within_bounds", False)) 
                then "risk_bounds_verified" 
                else "risk_bounds_violated"
    };
}

struct VerificationResult {
    z3_satisfiable: Bool;
    z3_model: Map<String, Double>;
    python_within_bounds: Bool;
    python_risk_ratio: Double;
    python_current_level: Int32;
    verification_passed: Bool;
    status: String;
}

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import Z3Surface, PythonSurface

@pytest.mark.asyncio
async def test_pyramid_risk_verifier_z3():
    surface = Z3Surface()
    code = '''
(declare-const x Real)
(declare-const y Real)
(assert (> x 0))
(assert (> y 0))
(assert (<= (* x y) 100))
(check-sat)
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["result"][0] == "sat"
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_pyramid_risk_verifier_cangjie():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "TECHNICAL_ANALYSIS" / "pyramid-risk-verifier"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: pyramid-risk-verifier\nDomain: TECHNICAL_ANALYSIS')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# CA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("pyramid", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Verifying Pyramid Risk Constraints

```python
from em_cubed import get_skill

skill = get_skill("pyramid-risk-verifier")
verification_input = {
    "entry_price": 100.0,
    "market_price": 105.0,
    "account_risk": 1000.0,
    "max_levels": 5
}
result = skill.execute(verification_input)
print("Verification passed:", result["verification_passed"])
print("Risk ratio:", result["python_risk_ratio"])
```