import pytest
import numpy as np

@pytest.mark.asyncio
async def test_bootstrap_ci_coverage():
    code = '''
import numpy as np
np.random.seed(42)
data = np.random.randn(100) * 10 + 50
boot_means = [np.mean(np.random.choice(data, 100, replace=True)) for _ in range(5000)]
lower = np.percentile(boot_means, 2.5)
upper = np.percentile(boot_means, 97.5)
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