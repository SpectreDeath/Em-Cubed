"""Direct test of run_isolated_eval outside pytest to compare behavior."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from em_cubed.surfaces.python_surface import run_isolated_eval, _build_restricted_interpreter

print("=== Direct call to run_isolated_eval ===")
result = run_isolated_eval("1 + 1", {}, timeout=10.0)
print("Result:", result)

result2 = run_isolated_eval("len([1,2,3])", {}, timeout=10.0)
print("len Result:", result2)

result3 = run_isolated_eval("while True: pass", {}, timeout=2.0)
print("Timeout Result:", result3)

print("\n=== Direct call to _build_restricted_interpreter in-process ===")
aeval = _build_restricted_interpreter({})
r = aeval('1 + 1')
print(f"in-process 1+1: {r}, errors: {aeval.error}")
