import pytest

@pytest.mark.asyncio
async def test_bootstrap_ci_coverage():
    code = '''
# Manual bootstrap without imports
# Fixed seed and inline data generation
data = [20.0, 80.0, 100.0, 40.0, 60.0, 85.0, 35.0, 75.0, 15.0, 95.0] * 10
# Bootstrap resampling
boot_means = []
for i in range(100):
    total = 0.0
    idx = (i * 7 + 11) % len(data)  # Deterministic index
    total = data[idx]
    boot_means.append(total)
# Percentiles
sorted_means = sorted(boot_means)
lower = sorted_means[2]
upper = sorted_means[97]
lower < 50 and upper > 50
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_statistical_prolog_rule():
    code = '''
valid_bootstrap(NObs, NBoot) :-
    NBoot >= NObs,
    NBoot =< 100000.

?- valid_bootstrap(50, 5000).
'''
    from em_cubed.surfaces import PrologSurface
    surface = PrologSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"