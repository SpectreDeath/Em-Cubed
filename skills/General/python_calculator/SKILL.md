---
name: Python Calculator
Domain: General
Version: 1.0.0
surfaces:
  - python
triggers:
  - calculator
  - math
  - arithmetic
  - computation
  - calculate
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
import math

# Trigonometric functions
angle_rad = math.radians(45)
sin_value = math.sin(angle_rad)  # Returns 0.707...

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
import math

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
    """Calculate square root using math.sqrt."""
    if x < 0:
        raise ValueError("Square root of negative number")
    return math.sqrt(x)

def factorial(n):
    """Calculate factorial of n."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial requires non-negative integer")
    return math.factorial(n)

def trigonometric_functions(angle_degrees):
    """Calculate sin, cos, tan of angle in degrees."""
    angle_rad = math.radians(angle_degrees)
    return {
        "sin": math.sin(angle_rad),
        "cos": math.cos(angle_rad),
        "tan": math.tan(angle_rad)
    }

def calculate_circle_area(radius):
    """Calculate area of circle."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2

def calculate_statistics(numbers):
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        raise ValueError("Empty list provided")

    n = len(numbers)
    mean = sum(numbers) / n
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)

    return {
        "count": n,
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "min": min(numbers),
        "max": max(numbers)
    }

# Example usage
if __name__ == "__main__":
    print("Basic arithmetic:")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")
    print(f"3 * 7 = {multiply(3, 7)}")
    print(f"15 / 3 = {divide(15, 3)}")

    print("\nAdvanced calculations:")
    print(f"2^8 = {power(2, 8)}")
    print(f"√16 = {square_root(16)}")
    print(f"5! = {factorial(5)}")

    print("\nTrigonometric functions (45°):")
    trig = trigonometric_functions(45)
    for func, value in trig.items():
        print(f"{func}: {value:.3f}")

    print(f"\nCircle area (r=5): {calculate_circle_area(5):.2f}")

    print("\nStatistics for [1, 2, 3, 4, 5]:")
    stats = calculate_statistics([1, 2, 3, 4, 5])
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
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
        assert result["value"] == 21

        result = await calculator.execute("15 / 3", {})
        assert result["status"] == "ok"
        assert result["value"] == 5.0

    async def test_power_operations(self, calculator):
        """Test power and root operations."""
        result = await calculator.execute("2 ** 8", {})
        assert result["status"] == "ok"
        assert result["value"] == 256

        # Test with math import
        result = await calculator.execute("import math; math.sqrt(16)", {})
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
            "import math; discriminant = b**2 - 4*a*c; (-b + math.sqrt(discriminant)) / (2*a)",
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
import math

# Statistical analysis
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = sum(data) / len(data)
variance = sum((x - mean) ** 2 for x in data) / len(data)
std_dev = math.sqrt(variance)

print(f"Mean: {mean:.2f}")
print(f"Standard deviation: {std_dev:.2f}")

# Matrix operations (basic)
matrix_a = [[1, 2], [3, 4]]
matrix_b = [[5, 6], [7, 8]]

# Simple matrix addition
result = []
for i in range(len(matrix_a)):
    row = []
    for j in range(len(matrix_a[0])):
        row.append(matrix_a[i][j] + matrix_b[i][j])
    result.append(row)

print("Matrix sum:", result)
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
- Em-Cubed framework for execution</content>
<parameter name="filePath">D:\GitHub\projects\em-cubed\skills\python_calculator\SKILL.md
