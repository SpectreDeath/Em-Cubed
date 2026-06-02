import pytest

@pytest.mark.asyncio
async def test_capacity_forecast():
    code = '''
# Inline forecast without numpy or random imports
# Use deterministic synthetic data
data = [100.0, 90.0, 110.0, 105.0, 95.0] * 20  # 100 elements
# Calculate mean
total = 0.0
for x in data:
    total += x
mean_val = total / len(data)
# Generate forecast
forecast = []
for i in range(30):
    forecast.append(mean_val)
len(forecast) == 30
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_bottleneck_detection():
    code = '''
current = 95
capacity = 100
threshold = 0.9
is_bottleneck = (current / capacity) > threshold
is_bottleneck
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert result["value"] is True

@pytest.mark.asyncio
async def test_capacity_prolog_rule():
    code = '''
resource_constraint(Capacity, Demand, Utilization) :-
    Utilization is Demand / Capacity,
    Utilization =< 0.9.

?- resource_constraint(100, 80, Util).
'''
    from em_cubed.surfaces import PrologSurface
    surface = PrologSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"