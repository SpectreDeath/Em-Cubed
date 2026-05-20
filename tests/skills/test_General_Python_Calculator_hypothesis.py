"""Property-based tests for Python Calculator skill using hypothesis."""

import pytest
from hypothesis import given, strategies as st

# Global variable to hold the asteval interpreter with the skill's functions defined
_aeval = None


def setup_module():
    """Set up the asteval interpreter with the Python Calculator skill's functions."""
    global _aeval
    from asteval import Interpreter
    _aeval = Interpreter()

    # Read the skill file and extract the Python code block
    skill_path = "D:/GitHub/projects/em-cubed/skills/General/python_calculator/SKILL.md"
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the Python code block (between ```python and ```)
    import re
    python_code_match = re.search(r"```python\s*\r?\n(.*?)```", content, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1).strip()
        # Execute the code to define the functions
        _aeval(python_code)
    else:
        raise ValueError("Could not find Python code block in SKILL.md")


def teardown_module():
    """Clean up the asteval interpreter."""
    global _aeval
    _aeval = None


def get_function(name):
    """Retrieve a function from the asteval symbol table."""
    global _aeval
    if _aeval is None:
        raise RuntimeError("Interpreter not initialized. Call setup_module first.")
    return _aeval.symtable.get(name)


@given(
    x=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_add_property(x, y):
    """Test that the add function returns the sum of x and y."""
    add_func = get_function("add")
    if add_func is None:
        pytest.skip("Add function not found in skill")
    result = add_func(x, y)
    # Due to floating point precision, we check if the result is close to the expected sum
    assert abs(result - (x + y)) < 1e-9


@given(
    a=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    b=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    c=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_square_root_property(a, b, c):
    """Test that the square_root function returns the square root of x for non-negative x."""
    # We'll test the square_root function with non-negative inputs
    sqrt_func = get_function("square_root")
    if sqrt_func is None:
        pytest.skip("Square root function not found in skill")
    # Generate non-negative x
    x = st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False).example()
    result = sqrt_func(x)
    expected = x ** 0.5
    assert abs(result - expected) < 1e-9


@given(
    n=st.integers(min_value=0, max_value=20),
)
def test_factorial_property(n):
    """Test that the factorial function returns n! for non-negative integers n."""
    factorial_func = get_function("factorial")
    if factorial_func is None:
        pytest.skip("Factorial function not found in skill")
    result = factorial_func(n)
    # Compute expected factorial
    expected = 1
    for i in range(1, n + 1):
        expected *= i
    assert result == expected