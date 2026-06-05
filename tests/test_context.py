"""Additional tests for the context/type system to improve coverage."""

from em_cubed.context import get_type_converter, get_type_registry, TypeDefinition, TypeRegistry, TypeConverter


def test_type_register_type():
    """Test registering a custom type."""
    registry = TypeRegistry()
    
    # Create a custom type definition
    custom_type = TypeDefinition(
        name="custom",
        python_type=str,
        prolog_term="custom",
        hy_form="custom",
        z3_sort="Custom",
        datalog_predicate="custom",
        to_python=lambda x: str(x),
        from_python=lambda x: x,
        to_prolog=lambda x: f"custom({x})",
        from_prolog=lambda x: x[7:-1],  # Remove custom( and )
        to_hy=lambda x: f"custom:{x}",
        from_hy=lambda x: x.split(":", 1)[1],
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: f"'{x}'",
        from_datalog=lambda x: x.strip("'")
    )
    
    registry.register_type(custom_type)
    assert "custom" in registry.list_types()
    retrieved = registry.get_type("custom")
    assert retrieved is not None
    assert retrieved.name == "custom"


def test_type_registry_get_type_returns_none_for_unknown():
    """Test that get_type returns None for unknown types."""
    registry = TypeRegistry()
    assert registry.get_type("nonexistent") is None


def test_type_converter_init_with_registry():
    """Test TypeConverter initialization with registry."""
    registry = TypeRegistry()
    converter = TypeConverter(registry)
    assert converter.registry is registry


def test_convert_to_surface_unknown_type_logs_warning():
    """Test that unknown type hints log warning and return value as-is."""
    converter = get_type_converter()
    # We can't easily test logging without capturing it, but we can verify behavior
    original = {"test": "value"}
    result = converter.convert_to_surface(original, "prolog", "unknown_type")
    assert result == original


def test_convert_from_surface_unknown_type_logs_warning():
    """Test that unknown type hints in convert_from_surface return value as-is."""
    converter = get_type_converter()
    original = [1, 2, 3]
    result = converter.convert_from_surface(original, "prolog", "unknown_type")
    assert result == original


def test_convert_to_surface_unknown_surface_logs_warning():
    """Test that unknown surfaces log warning and return value as-is."""
    converter = get_type_converter()
    original = 42
    result = converter.convert_to_surface(original, "unknown_surface", "integer")
    assert result == original


def test_convert_from_surface_unknown_surface_logs_warning():
    """Test that unknown surfaces in convert_from_surface return value as-is."""
    converter = get_type_converter()
    original = "test"
    result = converter.convert_from_surface(original, "unknown_surface", "string")
    assert result == original


def test_convert_to_surface_exception_handling():
    """Test that exceptions during conversion are caught and value returned as-is."""
    converter = get_type_converter()
    
    # Create a type definition with a faulty conversion function
    faulty_type = TypeDefinition(
        name="faulty",
        python_type=str,
        prolog_term="faulty",
        hy_form="faulty",
        z3_sort="Faulty",
        datalog_predicate="faulty",
        to_python=lambda x: x,  # This should work
        from_python=lambda x: x,
        to_prolog=lambda x: (_ for _ in ()).throw(ValueError("Test error")),  # This will raise
        from_prolog=lambda x: x,
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    registry = converter.registry
    registry.register_type(faulty_type)
    
    # When conversion fails, it should return the original value
    original = "test value"
    result = converter.convert_to_surface(original, "prolog", "faulty")
    assert result == original  # Should return original value on error


def test_convert_from_surface_exception_handling():
    """Test that exceptions during reverse conversion are caught and value returned as-is."""
    converter = get_type_converter()
    
    # Create a type definition with a faulty conversion function
    faulty_type = TypeDefinition(
        name="faulty_reverse",
        python_type=str,
        prolog_term="faulty_reverse",
        hy_form="faulty_reverse",
        z3_sort="FaultyReverse",
        datalog_predicate="faulty_reverse",
        to_python=lambda x: x,
        from_python=lambda x: x,
        to_prolog=lambda x: x,
        from_prolog=lambda x: (_ for _ in ()).throw(ValueError("Test error")),  # This will raise
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    registry = converter.registry
    registry.register_type(faulty_type)
    
    # When conversion fails, it should return the original value
    original = "test value"
    result = converter.convert_from_surface(original, "prolog", "faulty_reverse")
    assert result == original  # Should return original value on error


def test_infer_type_comprehensive():
    """Test type inference for various value types."""
    converter = get_type_converter()
    
    assert converter._infer_type(True) == "boolean"
    assert converter._infer_type(False) == "boolean"
    assert converter._infer_type(42) == "integer"
    assert converter._infer_type(3.14) == "float"
    assert converter._infer_type("hello") == "string"
    assert converter._infer_type([1, 2, 3]) == "list"
    assert converter._infer_type({"a": 1}) == "dict"
    assert converter._infer_type(set([1, 2, 3])) == "string"  # Default to string for unknown types
    assert converter._infer_type(object()) == "string"  # Default to string for unknown types


def test_initialize_type_system_idempotent():
    """Test that initialize_type_system can be called multiple times."""
    from em_cubed.context import initialize_type_system
    
    # Reset globals for clean test
    import em_cubed.context as context_module
    context_module._type_registry = None
    context_module._type_converter = None
    
    # Call multiple times
    initialize_type_system()
    first_registry = get_type_registry()
    first_converter = get_type_converter()
    
    initialize_type_system()
    second_registry = get_type_registry()
    second_converter = get_type_converter()
    
    # Should return the same instances
    assert first_registry is second_registry
    assert first_converter is second_converter


def test_type_definition_creation():
    """Test TypeDefinition creation and field access."""
    # Test creating a TypeDefinition with all fields
    def dummy_func(x):
        return x
        
    type_def = TypeDefinition(
        name="test_type",
        python_type=int,
        prolog_term="test",
        hy_form="test",
        z3_sort="Test",
        datalog_predicate="test",
        to_python=dummy_func,
        from_python=dummy_func,
        to_prolog=dummy_func,
        from_prolog=dummy_func,
        to_hy=dummy_func,
        from_hy=dummy_func,
        to_z3=dummy_func,
        from_z3=dummy_func,
        to_datalog=dummy_func,
        from_datalog=dummy_func
    )
    
    assert type_def.name == "test_type"
    assert type_def.python_type is int
    assert type_def.prolog_term == "test"
    assert type_def.hy_form == "test"
    assert type_def.z3_sort == "Test"
    assert type_def.datalog_predicate == "test"
    assert type_def.to_python == dummy_func
    assert type_def.from_python == dummy_func


def test_type_registry_list_types_empty():
    """Test list_types on empty registry."""
    # Create a registry without initializing basic types
    registry = TypeRegistry.__new__(TypeRegistry)  # Create instance without calling __init__
    registry._types = {}  # Manually empty the types dict
    assert registry.list_types() == []


def test_type_registry_register_duplicate_type():
    """Test registering a duplicate type overwrites the previous one."""
    registry = TypeRegistry()
    
    type1 = TypeDefinition(
        name="duplicate",
        python_type=str,
        prolog_term="str",
        hy_form="str",
        z3_sort="Str",
        datalog_predicate="str",
        to_python=lambda x: x,
        from_python=lambda x: x,
        to_prolog=lambda x: x,
        from_prolog=lambda x: x,
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    type2 = TypeDefinition(
        name="duplicate",
        python_type=int,
        prolog_term="int",
        hy_form="int",
        z3_sort="Int",
        datalog_predicate="int",
        to_python=lambda x: x,
        from_python=lambda x: x,
        to_prolog=lambda x: x,
        from_prolog=lambda x: x,
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    registry.register_type(type1)
    registry.register_type(type2)
    
    # Should have the basic types plus our duplicate type (so 7 total)
    # The duplicate type overwrites the first one, so we still have 6 basic + 1 duplicate = 7
    assert len(registry.list_types()) == 7
    assert "duplicate" in registry.list_types()
    
    # Should get the second type (the one that overwrote)
    retrieved = registry.get_type("duplicate")
    assert retrieved.python_type is int


def test_type_converter_convert_to_surface_all_surfaces():
    """Test convert_to_surface for all supported surfaces."""
    converter = get_type_converter()
    test_value = 42
    
    # Test python surface
    result = converter.convert_to_surface(test_value, "python", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test prolog surface
    result = converter.convert_to_surface(test_value, "prolog", "integer")
    assert result == "42"
    
    # Test hy surface
    result = converter.convert_to_surface(test_value, "hy", "integer")
    assert result == "42"
    
    # Test z3 surface
    result = converter.convert_to_surface(test_value, "z3", "integer")
    assert result == 42
    
    # Test datalog surface
    result = converter.convert_to_surface(test_value, "datalog", "integer")
    assert result == "42"


def test_type_converter_convert_from_surface_all_surfaces():
    """Test convert_from_surface for all supported surfaces."""
    converter = get_type_converter()
    
    # Test python surface
    result = converter.convert_from_surface(42, "python", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test prolog surface
    result = converter.convert_from_surface("42", "prolog", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test hy surface
    result = converter.convert_from_surface("42", "hy", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test z3 surface
    result = converter.convert_from_surface(42, "z3", "integer")
    assert result == 42
    assert isinstance(result, int)
    
    # Test datalog surface
    result = converter.convert_from_surface("42", "datalog", "integer")
    assert result == 42
    assert isinstance(result, int)


def test_type_converter_convert_with_type_inference():
    """Test conversion with automatic type inference."""
    converter = get_type_converter()
    
    # Test with integer value (should infer "integer" type)
    result = converter.convert_to_surface(123, "prolog")  # No type hint
    assert result == "123"
    
    # Test with string value (should infer "string" type)
    result = converter.convert_to_surface("hello", "prolog")  # No type hint
    assert result == '"hello"'
    
    # Test with boolean value (should infer "boolean" type)
    result = converter.convert_to_surface(True, "prolog")  # No type hint
    assert result == "true"
    
    # Test with list value (should infer "list" type)
    result = converter.convert_to_surface([1, 2, 3], "prolog")  # No type hint
    assert result == "[1,2,3]"
    
    # Test with dict value (should infer "dict" type)
    result = converter.convert_to_surface({"key": "value"}, "prolog")  # No type hint
    assert result == '{"key": "value"}'


def test_type_converter_round_trip_conversion():
    """Test round-trip conversion (to surface and back) for all types."""
    converter = get_type_converter()
    
    test_values = [
        (42, "integer"),
        (3.14, "float"),
        (True, "boolean"),
        ("hello", "string"),
        ([1, 2, 3], "list"),
        ({"key": "value"}, "dict")
    ]
    
    for value, type_hint in test_values:
        # Convert to prolog and back
        prolog_repr = converter.convert_to_surface(value, "prolog", type_hint)
        restored = converter.convert_from_surface(prolog_repr, "prolog", type_hint)
        assert restored == value, f"Round-trip failed for {type_hint}: {value} != {restored}"
        
        # Convert to hy and back
        hy_repr = converter.convert_to_surface(value, "hy", type_hint)
        restored = converter.convert_from_surface(hy_repr, "hy", type_hint)
        assert restored == value, f"Round-trip failed for {type_hint} (hy): {value} != {restored}"


def test_type_converter_edge_cases():
    """Test edge cases for type conversion."""
    converter = get_type_converter()
    
    # Test empty string
    result = converter.convert_to_surface("", "prolog", "string")
    assert result == '""'
    restored = converter.convert_from_surface(result, "prolog", "string")
    assert restored == ""
    
    # Test empty list
    result = converter.convert_to_surface([], "prolog", "list")
    assert result == "[]"
    restored = converter.convert_from_surface(result, "prolog", "list")
    assert restored == []
    
    # Test empty dict
    result = converter.convert_to_surface({}, "prolog", "dict")
    assert result == '{}'
    restored = converter.convert_from_surface(result, "prolog", "dict")
    assert restored == {}
    
    # Test nested structures
    nested = {"list": [1, 2, {"nested": "value"}], "string": "test"}
    result = converter.convert_to_surface(nested, "prolog", "dict")
    restored = converter.convert_from_surface(result, "prolog", "dict")
    assert restored == nested


def test_type_registry_get_type_case_sensitivity():
    """Test that get_type is case-sensitive."""
    registry = TypeRegistry()
    
    type_def = TypeDefinition(
        name="TestType",
        python_type=str,
        prolog_term="testtype",
        hy_form="testtype",
        z3_sort="TestType",
        datalog_predicate="testtype",
        to_python=lambda x: x,
        from_python=lambda x: x,
        to_prolog=lambda x: x,
        from_prolog=lambda x: x,
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    registry.register_type(type_def)
    
    # Should find with exact case
    assert registry.get_type("TestType") is not None
    
    # Should not find with different case
    assert registry.get_type("testtype") is None
    assert registry.get_type("TESTTYPE") is None


def test_type_registry_list_types_returns_copy():
    """Test that list_types returns a copy, not the internal list."""
    registry = TypeRegistry()
    
    type_def = TypeDefinition(
        name="test",
        python_type=str,
        prolog_term="test",
        hy_form="test",
        z3_sort="Test",
        datalog_predicate="test",
        to_python=lambda x: x,
        from_python=lambda x: x,
        to_prolog=lambda x: x,
        from_prolog=lambda x: x,
        to_hy=lambda x: x,
        from_hy=lambda x: x,
        to_z3=lambda x: x,
        from_z3=lambda x: x,
        to_datalog=lambda x: x,
        from_datalog=lambda x: x
    )
    
    registry.register_type(type_def)
    types_list = registry.list_types()
    
    # Modifying the returned list should not affect the internal state
    types_list.append("fake_type")
    assert "fake_type" not in registry.list_types()


def test_type_converter_logger_initialization():
    """Test that TypeConverter initializes logger correctly."""
    registry = TypeRegistry()
    converter = TypeConverter(registry)
    
    # Check that logger is bound with component name
    assert hasattr(converter, 'logger')
    # The logger should be a BoundLogger with component="type_converter"
    # We can't easily test the exact structure without exposing internals,
    # but we can verify it exists and is callable for basic logging
    assert callable(converter.logger.info)
    assert callable(converter.logger.error)
    assert callable(converter.logger.warning)
    assert callable(converter.logger.debug)


def test_global_type_system_singleton_behavior():
    """Test that global type system instances behave as singletons."""
    from em_cubed.context import get_type_registry, get_type_converter, initialize_type_system
    
    # Get instances multiple times
    registry1 = get_type_registry()
    registry2 = get_type_registry()
    converter1 = get_type_converter()
    converter2 = get_type_converter()
    
    # Should be the same instances
    assert registry1 is registry2
    assert converter1 is converter2
    
    # Initializing again should return the same instances
    initialize_type_system()
    assert get_type_registry() is registry1
    assert get_type_converter() is converter1


def test_type_converter_handle_none_value():
    """Test handling of None value in type conversion."""
    converter = get_type_converter()
    
    # None should be inferred as string type (default)
    result = converter.convert_to_surface(None, "prolog")
    # None becomes "None" string, then quoted for prolog
    assert result == '"None"'
    
    # Test with explicit string type hint
    result = converter.convert_to_surface(None, "prolog", "string")
    assert result == '"None"'
    
    # Test round-trip
    restored = converter.convert_from_surface(result, "prolog", "string")
    assert restored == "None"  # String "None", not actual None


def test_type_converter_handle_complex_objects():
    """Test handling of complex objects that don't match built-in types."""
    converter = get_type_converter()
    
    # Custom object
    class CustomObj:
        def __init__(self, value):
            self.value = value
        
        def __eq__(self, other):
            return isinstance(other, CustomObj) and self.value == other.value
    
    obj = CustomObj("test")
    
    # Should be treated as string (default fallback)
    result = converter.convert_to_surface(obj, "prolog")
    # The object will be converted to string via str()
    assert "'CustomObj'" in result or '"CustomObj"' in result or "CustomObj" in result
    
    # Test round-trip (will lose the object nature, but should not crash)
    restored = converter.convert_from_surface(result, "prolog", "string")
    assert isinstance(restored, str)