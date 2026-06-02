# Falling-Risk Pyramid — Cangjie Edition
# Orchestrates risk-adjusted position scaling with SQLite session tracking

import std.math.*

func main() {
    println("Falling-Risk Pyramid Starting...");
    
    let session_id = context["session_id"] as String;
    let entry_price = context["entry_price"] as Float64;
    let market_price = context.get("market_price", entry_price) as Float64;
    let account_risk = context.get("account_risk", 1000.0) as Float64;
    
    // SQLite: Track current pyramid state
    let sqlite_state = perform EmCubed.call_surface("sqlite", """
        CREATE TABLE IF NOT EXISTS pyramid_positions (
            session_id TEXT,
            level INTEGER,
            units INTEGER,
            entry_price REAL,
            stop_loss REAL,
            risk_per_unit REAL
        );
        
        SELECT level, units, entry_price FROM pyramid_positions 
        WHERE session_id = '{session_id}' ORDER BY level ASC;
    """);
    
    // Python: Compute pyramid levels
    let pyramid_result = perform EmCubed.call_surface("python", """
def compute_pyramid(entry_price, market_price, account_risk, max_levels=5):
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    base_units = account_risk / (0.01 * entry_price)
    
    positions = []
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        step = 0.005 * (level + 1)
        entry_adj = entry_price * (1 + step) if market_price > entry_price else entry_price * (1 - step)
        stop_loss = entry_price - (account_risk / (units * (max_levels - level))) if market_price > entry_price else entry_price + (account_risk / (units * (max_levels - level)))
        
        positions.append({{"level": level, "units": units, "entry": entry_adj, "stop_loss": stop_loss}})
    
    return {{"current_level": current_level, "positions": positions, "total_units": sum(p["units"] for p in positions)}}

compute_pyramid({entry_price}, {market_price}, {account_price}, 5)
""");
    
    return PyramidResult {
        current_level: pyramid_result.get("current_level", 0),
        total_units: pyramid_result.get("total_units", 0),
        positions: pyramid_result.get("positions", List<Map<String, Double>>()),
        status: pyramid_result.get("status", "computed")
    };
}

struct PyramidResult {
    current_level: Int32;
    total_units: Int32;
    positions: List<Map<String, Double>>;
    status: String;
}

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
async def test_falling_risk_pyramid():
    surface = PythonSurface()
    code = '''
def compute_pyramid(entry_price, market_price, account_risk, max_levels=5):
    price_distance = abs(market_price - entry_price)
    threshold = 0.001 * entry_price
    if price_distance < threshold:
        price_distance = threshold
    
    current_level = min(int(price_distance / (0.005 * entry_price)), max_levels - 1)
    base_units = account_risk / (0.01 * entry_price)
    
    positions = []
    for level in range(current_level + 1):
        scale_factor = 1.0 + 0.5 * level
        units = int(base_units * scale_factor)
        step = 0.005 * (level + 1)
        entry_adj = entry_price * (1 + step) if market_price > entry_price else entry_price * (1 - step)
        stop_loss = entry_price - (account_risk / (units * (max_levels - level))) if market_price > entry_price else entry_price + (account_risk / (units * (max_levels - level)))
        
        positions.append({"level": level, "units": units, "entry": entry_adj, "stop_loss": stop_loss})
    
    return {"current_level": current_level, "positions": positions, "total_units": sum(p["units"] for p in positions)}

result = compute_pyramid(100.0, 105.0, 1000.0, 5)
result["current_level"] >= 0 and result["total_units"] > 0
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
```

## Usage Patterns

### Computing Pyramid Scaling

```python
from em_cubed import get_skill

skill = get_skill("falling-risk-pyramid")
pyramid_input = {
    "session_id": "trading_session_001",
    "entry_price": 100.0,
    "market_price": 105.0,
    "account_risk": 1000.0
}
result = skill.execute(pyramid_input)
print("Current level:", result["current_level"], "Total units:", result["total_units"])
```