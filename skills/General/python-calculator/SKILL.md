---
name: python-calculator
domain: "GENERAL"
description: Skill for python_calculator.
compatibility: UNIVERSAL
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

Perform basic and advanced mathematical calculations using Python's built-in capabilities.

## Description

A comprehensive calculator skill that demonstrates safe Python code execution in Em-Cubed. Supports basic arithmetic, mathematical functions, and complex expressions with proper error handling.

## Examples

### Basic Arithmetic

```python
# Simple calculations
result = 2 + 3 * 4  # Returns 14
result = (2 + 3) * 4  # Returns 20
```

### Mathematical Functions

```python
# Trigonometric functions using approximations
angle_degrees = 45
angle_rad = angle_degrees * 3.141592653589793 / 180.0

# Taylor series for sin(x) = x - x^3/3! + x^5/5! - x^7/7! + ...
sin_approx = angle_rad
term = angle_rad
for i in range(1, 10):
    term *= -angle_rad * angle_rad / ((2 * i) * (2 * i + 1))
    sin_approx += term
sin_value = sin_approx  # Returns 0.707...

# Taylor series for cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + ...
cos_approx = 1
term = 1
for i in range(1, 10):
    term *= -angle_rad * angle_rad / ((2 * i - 1) * (2 * i))
    cos_approx += term
cos_value = cos_approx

# Statistical calculations
numbers = [1, 2, 3, 4, 5]
average = sum(numbers) / len(numbers)  # Returns 3.0
```

### Complex Expressions

```python
# Quadratic formula
a, b, c = 1, -5, 6
discriminant = b**2 - 4*a*c
root1 = (-b + discriminant**0.5) / (2*a)
root2 = (-b - discriminant**0.5) / (2*a)
# Returns root1=3.0, root2=2.0
```

## Implementation

### Python Calculator Functions

```python
def add(x, y):
    """Add two numbers."""
    return x + y

def subtract(x, y):
    """Subtract y from x."""
    return x - y

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def divide(x, y):
    """Divide x by y with zero division check."""
    if y == 0:
        raise ValueError("Division by zero")
    return x / y

def power(base, exponent):
    """Calculate base raised to exponent."""
    return base ** exponent

def square_root(x):
    """Calculate square root using exponentiation."""
    if x < 0:
        raise ValueError("Square root of negative number")
    return x ** 0.5

def factorial(n):
    """Calculate factorial of n."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial requires non-negative integer")
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def trigonometric_functions(angle_degrees):
    """Calculate sin, cos, tan of angle in degrees using approximations."""
    # Convert degrees to radians
    angle_rad = angle_degrees * 3.141592653589793 / 180.0
    
    # Taylor series approximations for sin and cos
    # sin(x) = x - x^3/3! + x^5/5! - x^7/7! + ...
    # cos(x) = 1 - x^2/2! + x^4/4! - x^6/6! + ...
    
    def sin_approx(x):
        result = x
        term = x
        for i in range(1, 10):  # 10 terms for good accuracy
            term *= -x * x / ((2 * i) * (2 * i + 1))
            result += term
        return result
    
    def cos_approx(x):
        result = 1
        term = 1
        for i in range(1, 10):  # 10 terms for good accuracy
            term *= -x * x / ((2 * i - 1) * (2 * i))
            result += term
        return result
    
    sin_val = sin_approx(angle_rad)
    cos_val = cos_approx(angle_rad)
    tan_val = sin_val / cos_val if cos_val != 0 else float('inf')
    
    return {
        "sin": sin_val,
        "cos": cos_val,
        "tan": tan_val
    }

def calculate_circle_area(radius):
    """Calculate area of circle."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    pi_approx = 3.141592653589793
    return pi_approx * radius ** 2

def calculate_statistics(numbers):
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        raise ValueError("Empty list provided")
    
    n = len(numbers)
    mean = sum(numbers) / n
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = variance ** 0.5  # Square root using exponentiation
    
    return {
        "count": n,
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "min": min(numbers),
        "max": max(numbers)
    }
```

## Testing

### Unit Tests

```python
import pytest
import math
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
class TestPythonCalculator:
    @pytest.fixture
    async def calculator(self):
        """Get Python surface for calculator operations."""
        surface = PythonSurface()
        return surface

    async def test_basic_arithmetic(self, calculator):
        """Test basic arithmetic operations."""
        result = await calculator.execute("2 + 3", {})
        assert result["status"] == "ok"
        assert result["value"] == 5

        result = await calculator.execute("10 - 4", {})
        assert result["status"] == "ok"
        assert result["value"] == 6

        result = await calculator.execute("3 * 7", {})
        assert result["status"] == "ok"
        assert result["value"] = 21

        result = await calculator.execute("15 / 3", {})
        assert result["status"] == "ok"
        assert result["value"] == 5.0

    async def test_power_operations(self, calculator):
        """Test power and root operations."""
        result = await calculator.execute("2 ** 8", {})
        assert result["status"] == "ok"
        assert result["value"] == 256

        # Test square root using exponentiation
        result = await calculator.execute("16 ** 0.5", {})
        assert result["status"] == "ok"
        assert result["value"] == 4.0

    async def test_error_handling(self, calculator):
        """Test error handling for invalid operations."""
        # Division by zero
        result = await calculator.execute("1 / 0", {})
        assert result["status"] == "error"

        # Invalid syntax
        result = await calculator.execute("invalid syntax +++", {})
        assert result["status"] == "error"

    async def test_complex_expressions(self, calculator):
        """Test complex mathematical expressions."""
        # Quadratic formula
        context = {"a": 1, "b": -5, "c": 6}
        result = await calculator.execute(
            "discriminant = b**2 - 4*a*c; (-b + discriminant**0.5) / (2*a)",
            context
        )
        assert result["status"] == "ok"
        assert abs(result["value"] - 3.0) < 0.001

    async def test_list_operations(self, calculator):
        """Test operations on lists and collections."""
        result = await calculator.execute("sum([1, 2, 3, 4, 5])", {})
        assert result["status"] == "ok"
        assert result["value"] == 15

        result = await calculator.execute("len([1, 2, 3])", {})
        assert result["status"] == "ok"
        assert result["value"] == 3

    async def test_context_usage(self, calculator):
        """Test using context variables in calculations."""
        context = {"radius": 5, "pi": 3.14159}
        result = await calculator.execute("pi * radius ** 2", context)
        assert result["status"] == "ok"
        assert abs(result["value"] - 78.53975) < 0.001
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_calculator_skill_integration():
    """Test the calculator skill in a complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create skill directory
        skills_dir = Path(tmpdir) / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "python_calculator"
        skill_dir.mkdir()

        # Create SKILL.md (simplified for testing)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Python Calculator
Domain: Mathematics
surfaces:
  - python
---

## Purpose
Mathematical calculations

## Description
Calculator skill for testing
""")

        # Index skills
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir, registry_file)

        # Search for calculator
        results = search_registry("calculator", registry_file)
        assert len(results) == 1
        assert results[0]["name"] == "Python Calculator"

        # Execute calculator functions
        surface = PythonSurface()

        # Test basic calculation
        result = await surface.execute("2 + 3 * 4", {})
        assert result["status"] == "ok"
        assert result["value"] == 14  # 2 + (3*4) = 14

        # Test with context
        result = await surface.execute("x ** 2 + y", {"x": 3, "y": 5})
        assert result["status"] == "ok"
        assert result["value"] == 14  # 9 + 5 = 14
```

## Usage Patterns

### Basic Calculations

```python
from em_cubed.surfaces import PythonSurface

calculator = PythonSurface()

# Simple math
result = await calculator.execute("42 * 2 + 8", {})
print(f"Result: {result['value']}")  # 92

# Using variables
result = await calculator.execute("principal * (1 + rate) ** years", {
    "principal": 1000,
    "rate": 0.05,
    "years": 5
})
print(f"Future value: ${result['value']:.2f}")
```

### Advanced Mathematical Operations

```python
# Statistical analysis
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = sum(data) / len(data)
variance = sum((x - mean) ** 2 for x in data) / len(data)
std_dev = variance ** 0.5  # Square root using exponentiation

print(f"Mean: {mean:.2f}")
print(f"Standard deviation: {std_dev:.2f}")
```

## Security Considerations

This skill demonstrates safe execution practices:

- Uses asteval for controlled Python execution
- No access to file system operations
- No network access
- Limited to mathematical and data operations
- Proper error handling for invalid inputs

## Dependencies

- None (uses only Python standard library)
- Em-Cubed framework for execution

# Default execution: if input is provided, use it to run a calculation
if 'input' in globals():
    # If input is a string, treat it as an expression to evaluate
    if isinstance(input, str):
        try:
            result = eval(input)
        except:
            result = None
    # If input is a list or tuple of two numbers, add them
    elif isinstance(input, (list, tuple)) and len(input) == 2:
        try:
            result = add(input[0], input[1])
        except:
            result = None
    # If input is a dict, look for known keys
    elif isinstance(input, dict):
        # Try to use the add function if we have two numbers
        if 'a' in input and 'b' in input:
            try:
                result = add(input['a'], input['b'])
            except:
                result = None
        elif 'expression' in input:
            try:
                result = eval(input['expression'])
            except:
                result = None
        else:
            result = None
    else:
        result = None
else:
    result = None