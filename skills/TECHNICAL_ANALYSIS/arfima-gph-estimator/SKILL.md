---
name: ARFIMA GPH Estimator
domain: TECHNICAL_ANALYSIS
version: 1.0.0
surfaces:
  - sqlite
  - python
---

## Purpose
Estimates the fractional integration parameter d using Geweke and Porter-Hudak (GPH) log-periodogram regression.

## Description
Extracts long-memory characteristics from a time series session. It isolates historical log returns within an in-memory SQLite table, computes periodogram ordinates for the lower frequencies ($g(n) = n^\alpha$), and applies a safe linear regression in Python to output the fractional differencing parameter $d$ alongside an $R^2$ confidence score.

## Implementation

### SQLite
```sql
CREATE TABLE IF NOT EXISTS session_returns (
    session_id TEXT,
    timestamp INTEGER,
    log_return REAL
);

DELETE FROM session_returns 
WHERE session_id = :session_id 
  AND timestamp < (SELECT MAX(timestamp) FROM session_returns WHERE session_id = :session_id) - 300;

SELECT log_return FROM session_returns 
WHERE session_id = :session_id 
ORDER BY timestamp ASC;
```

### Python
```python
def calculate_gph(returns):
    n = len(returns)
    if n < 32:
        return {"d": 0.0, "r_squared": 0.0, "status": "insufficient_data"}
    
    total = 0.0
    for r in returns:
        total += r
    mean = total / n
    
    m = int(n ** 0.5)
    pi_val = 3.141592653589793
    
    y_harmics = []
    x_frequencies = []
    
    for k in range(1, m + 1):
        cos_sum = 0.0
        sin_sum = 0.0
        for t in range(n):
            angle = (2.0 * pi_val * k * (t + 1)) / n
            diff = returns[t] - mean
            cos_sum += diff * cos(angle)
            sin_sum += diff * sin(angle)
            
        periodogram = (cos_sum**2 + sin_sum**2) / (2.0 * pi_val * n)
        
        if periodogram > 0:
            y_harmics.append(log(periodogram))
            lambda_k = (2.0 * pi_val * k) / n
            x_frequencies.append(-2.0 * log(2.0 * sin(lambda_k / 2.0)))
    
    m_valid = len(y_harmics)
    if m_valid < 2:
        return {"d": 0.0, "r_squared": 0.0, "status": "regression_failed"}
        
    sum_x = 0.0
    sum_y = 0.0
    for i in range(m_valid):
        sum_x += x_frequencies[i]
        sum_y += y_harmics[i]
        
    mean_x = sum_x / m_valid
    mean_y = sum_y / m_valid
    
    num = 0.0
    den = 0.0
    for i in range(m_valid):
        dx = x_frequencies[i] - mean_x
        dy = y_harmics[i] - mean_y
        num += dx * dy
        den += dx * dx
        
    if den == 0:
        return {"d": 0.0, "r_squared": 0.0, "status": "collinear"}
        
    d_estimator = num / den
    
    total_ss = 0.0
    residual_ss = 0.0
    for i in range(m_valid):
        pred_y = mean_y + d_estimator * (x_frequencies[i] - mean_x)
        total_ss += (y_harmics[i] - mean_y) ** 2
        residual_ss += (y_harmics[i] - pred_y) ** 2
        
    r2 = 1.0 - (residual_ss / total_ss) if total_ss > 0 else 0.0
    
    return {"d": d_estimator, "r_squared": r2, "status": "success"}

calculate_gph(series_data)
```