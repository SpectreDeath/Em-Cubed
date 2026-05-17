"""Unified type system for cross-surface data exchange.

This module provides automatic serialization/deserialization and type validation
for data moving between different execution surfaces (Python, Prolog, Hy, Z3, Datalog).
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union
import structlog

logger = structlog.get_logger()

T = TypeVar('T')


@dataclass
class TypeDefinition:
    """Definition of a data type for cross-surface exchange."""
    name: str
    python_type: type
    prolog_term: str  # How to represent in Prolog
    hy_form: str      # How to represent in Hy Lisp
    z3_sort: str      # Z3 sort representation
    datalog_predicate: str  # Datalog predicate name
    
    # Conversion functions
    to_python: callable
    from_python: callable
    to_prolog: callable
    from_prolog: callable
    to_hy: callable
    from_hy: callable
    to_z3: callable
    from_z3: callable
    to_datalog: callable
    from_datalog: callable


class TypeRegistry:
    """Registry of type definitions for cross-surface conversion."""
    
    def __init__(self):
        self._types: Dict[str, TypeDefinition] = {}
        self._initialize_basic_types()
    
    def _initialize_basic_types(self):
        """Initialize basic type definitions."""
        # Integer type
        self.register_type(TypeDefinition(
            name="integer",
            python_type=int,
            prolog_term="integer",
            hy_form="integer",
            z3_sort="Int",
            datalog_predicate="int",
            to_python=lambda x: int(x),
            from_python=lambda x: x,
            to_prolog=lambda x: str(int(x)),
            from_prolog=lambda x: int(x),
            to_hy=lambda x: str(int(x)),
            from_hy=lambda x: int(x),
            to_z3=lambda x: int(x),
            from_z3=lambda x: int(x),
            to_datalog=lambda x: str(int(x)),
            from_datalog=lambda x: int(x)
        ))
        
        # Float type
        self.register_type(TypeDefinition(
            name="float",
            python_type=float,
            prolog_term="float",
            hy_form="float",
            z3_sort="Real",
            datalog_predicate="float",
            to_python=lambda x: float(x),
            from_python=lambda x: x,
            to_prolog=lambda x: str(float(x)),
            from_prolog=lambda x: float(x),
            to_hy=lambda x: str(float(x)),
            from_hy=lambda x: float(x),
            to_z3=lambda x: float(x),
            from_z3=lambda x: float(x),
            to_datalog=lambda x: str(float(x)),
            from_datalog=lambda x: float(x)
        ))
        
        # Boolean type
        self.register_type(TypeDefinition(
            name="boolean",
            python_type=bool,
            prolog_term="boolean",
            hy_form="boolean",
            z3_sort="Bool",
            datalog_predicate="bool",
            to_python=lambda x: bool(x),
            from_python=lambda x: x,
            to_prolog=lambda x: "true" if bool(x) else "false",
            from_prolog=lambda x: x.lower() == "true",
            to_hy=lambda x: "true" if bool(x) else "false",
            from_hy=lambda x: x.lower() == "true",
            to_z3=lambda x: bool(x),
            from_z3=lambda x: bool(x),
            to_datalog=lambda x: "true" if bool(x) else "false",
            from_datalog=lambda x: x.lower() == "true"
        ))
        
        # String type
        self.register_type(TypeDefinition(
            name="string",
            python_type=str,
            prolog_term="string",
            hy_form="string",
            z3_sort="String",
            datalog_predicate="str",
            to_python=lambda x: str(x),
            from_python=lambda x: x,
            to_prolog=lambda x: f'"{str(x)}"',
            from_prolog=lambda x: x.strip('"'),
            to_hy=lambda x: f'"{str(x)}"',
            from_hy=lambda x: x.strip('"'),
            to_z3=lambda x: str(x),
            from_z3=lambda x: str(x),
            to_datalog=lambda x: f'"{str(x)}"',
            from_datalog=lambda x: x.strip('"')
        ))
        
        # List type
        self.register_type(TypeDefinition(
            name="list",
            python_type=list,
            prolog_term="list",
            hy_form="list",
            z3_sort="Array Int",  # Simplified - in practice would be parameterized
            datalog_predicate="list",
            to_python=lambda x: list(x) if not isinstance(x, list) else x,
            from_python=lambda x: x,
            to_prolog=lambda x: f"[{','.join(str(i) for i in x)}]",
            from_prolog=lambda x: [int(i.strip()) for i in x.strip('[]').split(',') if i.strip()],
            to_hy=lambda x: f"[{','.join(str(i) for i in x)}]",
            from_hy=lambda x: [int(i.strip()) for i in x.strip('[]').split(',') if i.strip()],
            to_z3=lambda x: x,  # Would need proper Z3 array handling
            from_z3=lambda x: list(x),
            to_datalog=lambda x: f"[{','.join(str(i) for i in x)}]",
            from_datalog=lambda x: [int(i.strip()) for i in x.strip('[]').split(',') if i.strip()]
        ))
        
        # Dictionary/Map type
        self.register_type(TypeDefinition(
            name="dict",
            python_type=dict,
            prolog_term="dict",
            hy_form="dict",
            z3_sort="Map Int Int",  # Simplified
            datalog_predicate="dict",
            to_python=lambda x: dict(x) if not isinstance(x, dict) else x,
            from_python=lambda x: x,
            to_prolog=lambda x: json.dumps(x),
            from_prolog=lambda x: json.loads(x),
            to_hy=lambda x: json.dumps(x),
            from_hy=lambda x: json.loads(x),
            to_z3=lambda x: x,  # Would need proper Z3 map handling
            from_z3=lambda x: dict(x),
            to_datalog=lambda x: json.dumps(x),
            from_datalog=lambda x: json.loads(x)
        ))
    
    def register_type(self, type_def: TypeDefinition):
        """Register a type definition."""
        self._types[type_def.name] = type_def
        logger.debug("Registered type", type_name=type_def.name)
    
    def get_type(self, name: str) -> Optional[TypeDefinition]:
        """Get a type definition by name."""
        return self._types.get(name)
    
    def list_types(self) -> List[str]:
        """List all registered type names."""
        return list(self._types.keys())


class TypeConverter:
    """Handles conversion between Python and surface-specific representations."""
    
    def __init__(self, type_registry: TypeRegistry):
        self.registry = type_registry
        self.logger = logger.bind(component="type_converter")
    
    def convert_to_surface(self, value: Any, surface: str, type_hint: Optional[str] = None) -> Any:
        """Convert a Python value to surface-specific representation.
        
        Args:
            value: The Python value to convert
            surface: Target surface name (python, prolog, hy, z3, datalog)
            type_hint: Optional hint about the expected type
            
        Returns:
            Surface-specific representation of the value
        """
        # If no type hint, try to infer
        if type_hint is None:
            type_hint = self._infer_type(value)
        
        type_def = self.registry.get_type(type_hint)
        if not type_def:
            self.logger.warning("Unknown type hint, returning value as-is", 
                              type_hint=type_hint)
            return value
        
        # Convert based on target surface
        try:
            if surface == "python":
                return type_def.to_python(value)
            elif surface == "prolog":
                return type_def.to_prolog(value)
            elif surface == "hy":
                return type_def.to_hy(value)
            elif surface == "z3":
                return type_def.to_z3(value)
            elif surface == "datalog":
                return type_def.to_datalog(value)
            else:
                self.logger.warning("Unknown surface, returning value as-is", 
                                  surface=surface)
                return value
        except Exception as e:
            self.logger.error("Failed to convert value to surface", 
                            value=value, surface=surface, type_hint=type_hint, error=str(e))
            # Return original value as fallback
            return value
    
    def convert_from_surface(self, value: Any, surface: str, type_hint: Optional[str] = None) -> Any:
        """Convert a surface-specific value to Python representation.
        
        Args:
            value: The surface-specific value to convert
            surface: Source surface name (python, prolog, hy, z3, datalog)
            type_hint: Optional hint about the expected type
            
        Returns:
            Python representation of the value
        """
        # If no type hint, try to infer
        if type_hint is None:
            type_hint = self._infer_type(value)
        
        type_def = self.registry.get_type(type_hint)
        if not type_def:
            self.logger.warning("Unknown type hint, returning value as-is", 
                              type_hint=type_hint)
            return value
        
        # Convert based on source surface
        try:
            if surface == "python":
                return type_def.from_python(value)
            elif surface == "prolog":
                return type_def.from_prolog(value)
            elif surface == "hy":
                return type_def.from_hy(value)
            elif surface == "z3":
                return type_def.from_z3(value)
            elif surface == "datalog":
                return type_def.from_datalog(value)
            else:
                self.logger.warning("Unknown surface, returning value as-is", 
                                  surface=surface)
                return value
        except Exception as e:
            self.logger.error("Failed to convert value from surface", 
                            value=value, surface=surface, type_hint=type_hint, error=str(e))
            # Return original value as fallback
            return value
    
    def _infer_type(self, value: Any) -> str:
        """Infer the type of a value.
        
        Args:
            value: The value to infer type for
            
        Returns:
            Type name string
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            # Default to string for unknown types
            return "string"


# Global type system instances
_type_registry: Optional[TypeRegistry] = None
_type_converter: Optional[TypeConverter] = None


def get_type_registry() -> TypeRegistry:
    """Get the global type registry instance."""
    global _type_registry
    if _type_registry is None:
        _type_registry = TypeRegistry()
    return _type_registry


def get_type_converter() -> TypeConverter:
    """Get the global type converter instance."""
    global _type_converter
    if _type_converter is None:
        _type_converter = TypeConverter(get_type_registry())
    return _type_converter


def initialize_type_system():
    """Initialize the global type system."""
    get_type_registry()  # Creates registry if needed
    get_type_converter()  # Creates converter if needed
    logger.info("Type system initialized")