"""Tests for the context/type system."""
import pytest

from em_cubed.context import get_type_converter, get_type_registry, initialize_type_system


def test_type_system_initialization():
    """Test that the type system can be initialized."""
    initialize_type_system()
    assert get_type_registry() is not None
    assert get_type_converter() is not None


def test_type_registry_basic_types():
    """Test that basic types are registered."""
    registry = get_type_registry()
    types = registry.list_types()
    
    expected_types = ["integer", "float", "boolean", "string", "list", "dict"]
    for expected in expected_types:
        assert expected in types, f"Expected type {expected} not found in {types}"


def test_type_converter_python_to_prolog():
    """Test conversion from Python to Prolog representation."""
    converter = get_type_converter()
    
    # Test integer
    result = converter.convert_to_surface(42, "prolog", "integer")
    assert result == "42"
    
    # Test boolean
    result = converter.convert_to_surface(True, "prolog", "boolean")
    assert result == "true"
    
    result = converter.convert_to_surface(False, "prolog", "boolean")
    assert result == "false"
    
    # Test string
    result = converter.convert_to_surface("hello", "prolog", "string")
    assert result == '"hello"'
    
    # Test list
    result = converter.convert_to_surface([1, 2, 3], "prolog", "list")
    assert result == "[1,2,3]"
    
    # Test dict
    result = converter.convert_to_surface({"key": "value"}, "prolog", "dict")
    assert result == '{"key": "value"}'


def test_type_converter_prolog_to_python():
    """Test conversion from Prolog to Python representation."""
    converter = get_type_converter()
    
    # Test integer
    result = converter.convert_from_surface("42", "prolog", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test boolean
    result = converter.convert_from_surface("true", "prolog", "boolean")
    assert result is True
    assert isinstance(result, bool)
    
    result = converter.convert_from_surface("false", "prolog", "boolean")
    assert result is False
    assert isinstance(result, bool)
    
    # Test string
    result = converter.convert_from_surface('"hello"', "prolog", "string")
    assert result == "hello"
    assert isinstance(result, str)
    
    # Test list
    result = converter.convert_from_surface("[1,2,3]", "prolog", "list")
    assert result == [1, 2, 3]
    assert isinstance(result, list)
    
    # Test dict
    result = converter.convert_from_surface('{"key": "value"}', "prolog", "dict")
    assert result == {"key": "value"}
    assert isinstance(result, dict)


def test_type_converter_bidirectional():
    """Test that conversions work bidirectionally."""
    converter = get_type_converter()
    
    # Test integer round-trip
    original = 42
    prolog_repr = converter.convert_to_surface(original, "prolog", "integer")
    restored = converter.convert_from_surface(prolog_repr, "prolog", "integer")
    assert restored == original
    
    # Test string round-trip
    original = "hello world"
    prolog_repr = converter.convert_to_surface(original, "prolog", "string")
    restored = converter.convert_from_surface(prolog_repr, "prolog", "string")
    assert restored == original
    
    # Test list round-trip
    original = [1, 2, 3, 4, 5]
    prolog_repr = converter.convert_to_surface(original, "prolog", "list")
    restored = converter.convert_from_surface(prolog_repr, "prolog", "list")
    assert restored == original


def test_type_converter_unknown_type():
    """Test handling of unknown types."""
    converter = get_type_converter()
    
    # With unknown type, should return value as-is
    original = {"custom": "object"}
    result = converter.convert_to_surface(original, "prolog", "unknown_type")
    assert result == original
    
    result = converter.convert_from_surface(original, "prolog", "unknown_type")
    assert result == original


def test_type_converter_unknown_surface():
    """Test handling of unknown surfaces."""
    converter = get_type_converter()
    
    # With unknown surface, should return value as-is
    original = 42
    result = converter.convert_to_surface(original, "unknown_surface", "integer")
    assert result == original
    
    result = converter.convert_from_surface(original, "unknown_surface", "integer")
    assert result == original


if __name__ == "__main__":
    test_type_system_initialization()
    test_type_registry_basic_types()
    test_type_converter_python_to_prolog()
    test_type_converter_prolog_to_python()
    test_type_converter_bidirectional()
    test_type_converter_unknown_type()
    test_type_converter_unknown_surface()
    print("All tests passed!")