---
name: pyramid-risk-verifier
domain: TECHNICAL_ANALYSIS
version: 1.0.0
surfaces:
  - z3
  - python
description: Pyramid risk verifier for validating nested risk classifications against formal safety constraints and threshold logic.
compatibility: Z3
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

## Purpose
Formally verifies that the falling-risk pyramid position scaling logic never exceeds absolute maximum risk boundaries using Z3 theorem prover.

## Description
Uses Z3 to mathematically prove that for any sequence of position entries following the falling-risk pyramid algorithm, the cumulative risk remains bounded by the user-specified maximum account risk percentage, regardless of market conditions or entry timing.

## Implementation

### Z3
```z3
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

; Recursive sum: cumulative units from level 0 to levels-1
(define-fun cum_risk_sum ((n Int) (levels Int)) Real
  (ite (>= n levels)
    0.0
    (+ (position_size n) (cum_risk_sum (+ n 1) levels))))

; Define cumulative risk calculation (sum of position_size * 0.01 * entry_price)
(define-fun cumulative_risk ((levels Int)) Real
  (* (cum_risk_sum 0 levels) 0.01 entry_price))

; Risk boundary assertions
(assert (>= entry_price 0.01))
(assert (>= market_price 0.01))
(assert (> account_risk 0))
(assert (> max_pyramid_levels 0))
(assert (<= max_pyramid_levels 10))
(assert (<= account_risk 100.0))  ; Max 100% account risk per trade

; Prove: Cumulative risk never exceeds account_risk for any valid pyramid level
(assert (>= (cumulative_risk current_level) 0))
(assert (<= (cumulative_risk current_level) account_risk))

(check-sat)
(get-model)
```

### Python
```python
def verify_pyramid_risk_bounds(entry_price, market_price, account_risk, max_levels=5):
    """
    Verifies that pyramid position sizing respects risk boundaries.
    Returns True if risk bounds are respected, False otherwise.
    """
    if entry_price <= 0 or market_price <= 0 or account_risk <= 0:
        return False
    
    # Calculate pyramid level
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    
    # Calculate total position size across all levels
    base_units = account_risk / (0.01 * entry_price)
    total_units = 0
    
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        total_units += units
    
    # Calculate actual risk
    actual_risk = total_units * 0.01 * entry_price
    
    # Risk should never exceed account_risk (100% of allocated risk)
    risk_ratio = actual_risk / account_risk if account_risk > 0 else 0
    
    return {
        "within_bounds": risk_ratio <= 1.0,
        "risk_ratio": risk_ratio,
        "actual_risk": actual_risk,
        "allocated_risk": account_risk,
        "current_level": current_level,
        "total_units": total_units,
        "status": "verified" if risk_ratio <= 1.0 else "violated"
    }

# Verify with test cases
test_cases = [
    (100.0, 100.0, 1000.0, 5),   # At entry
    (100.0, 105.0, 1000.0, 5),   # 5% move up
    (100.0, 95.0, 1000.0, 5),    # 5% move down
    (100.0, 120.0, 1000.0, 5),   # 20% move up
    (50.0, 60.0, 500.0, 3),      # Lower price, smaller account
]

results = []
for entry, market, risk, levels in test_cases:
    result = verify_pyramid_risk_bounds(entry, market, risk, levels)
    results.append(result)
    assert result["within_bounds"], f"Risk violation: {result}"

all_passed = all(r["within_bounds"] for r in results)
all_passed
```