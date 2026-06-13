---
name: falling-risk-pyramid
domain: TECHNICAL_ANALYSIS
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Falling risk pyramid for stratified risk classification using nested threshold rules and decision boundaries.
compatibility: PYTHON
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
Computes position sizes using a falling-risk pyramid model where risk decreases as price moves favorably.

## Description
Implements dynamic position scaling based on distance from entry. As price moves favorably, position size increases while risk per unit decreases. Uses SQLite to track open positions and Python to compute the risk-adjusted scaling levels.

## Implementation

### Python
```python
def compute_pyramid(entry_price, market_price, account_risk, max_pyramid_levels):
    price_distance = abs(market_price - entry_price)
    if price_distance < 0.001 * entry_price:
        price_distance = 0.001 * entry_price
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_pyramid_levels - 1)
    
    base_units = account_risk / (0.01 * entry_price)
    
    positions = []
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        stop_distance = max_pyramid_levels - level
        risk_per_unit = account_risk / (units * stop_distance) if units > 0 else account_risk
        positions.append({
            "level": level,
            "units": units,
            "entry": entry_price * (1 + 0.005 * level) if market_price > entry_price else entry_price * (1 - 0.005 * level),
            "stop_loss": entry_price * (1 - 0.01 * (max_pyramid_levels - level)) if market_price > entry_price else entry_price * (1 + 0.01 * (max_pyramid_levels - level)),
            "risk_per_unit": risk_per_unit,
            "total_risk": units * risk_per_unit
        })
    
    return {
        "current_level": current_level,
        "positions": positions,
        "total_units": sum(p["units"] for p in positions),
        "remaining_capacity": max_pyramid_levels - current_level,
        "status": "success"
    }

compute_pyramid(entry_price, market_price, account_risk, 5)
```

### SQLite
```sql
CREATE TABLE IF NOT EXISTS pyramid_positions (
    session_id TEXT,
    level INTEGER,
    units INTEGER,
    entry_price REAL,
    stop_loss REAL,
    risk_per_unit REAL,
    total_risk REAL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

INSERT INTO pyramid_positions (session_id, level, units, entry_price, stop_loss, risk_per_unit, total_risk)
VALUES (:session_id, :level, :units, :entry_price, :stop_loss, :risk_per_unit, :total_risk);

SELECT level, units, entry_price, stop_loss, total_risk 
FROM pyramid_positions 
WHERE session_id = :session_id 
ORDER BY level ASC;
```