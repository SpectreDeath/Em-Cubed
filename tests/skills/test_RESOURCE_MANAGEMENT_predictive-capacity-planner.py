import pytest
import numpy as np

@pytest.mark.asyncio
async def test_capacity_forecast():
    code = '''
import numpy as np

data = np.random.randn(100) * 10 + 100
np.random.seed(42)
forecast = [np.mean(data) for _ in range(30)]
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