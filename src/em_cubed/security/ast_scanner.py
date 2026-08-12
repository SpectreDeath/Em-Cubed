"""AST Security Static Analyzer for Em-Cubed Skill Engine.

Audits Python skill scripts before execution to detect unauthorized imports,
dangerous system calls, file manipulation, or dynamic evaluation exploits.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class SecurityViolation:
    """Security violation item detected during AST scanning."""
    line: int
    column: int
    rule: str
    message: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW


@dataclass
class ScanReport:
    """Result report of AST security scan."""
    is_safe: bool
    violations: List[SecurityViolation] = field(default_factory=list)


class ASTSecurityScanner(ast.NodeVisitor):
    """AST Visitor scanning Python code for unsafe operations."""

    BLOCKED_MODULES: Set[str] = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "ctypes",
        "builtins",
        "importlib",
        "pickle",
        "shelve",
        "tempfile",
    }

    BLOCKED_FUNCTIONS: Set[str] = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "getattr",
        "setattr",
        "delattr",
    }

    def __init__(self, allowed_modules: Optional[Set[str]] = None) -> None:
        self.allowed_modules = allowed_modules or set()
        self.violations: List[SecurityViolation] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_base = alias.name.split(".")[0]
            if module_base in self.BLOCKED_MODULES and module_base not in self.allowed_modules:
                self.violations.append(
                    SecurityViolation(
                        line=node.lineno,
                        column=node.col_offset,
                        rule="BLOCKED_IMPORT",
                        message=f"Forbidden module import detected: '{alias.name}'",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            module_base = node.module.split(".")[0]
            if module_base in self.BLOCKED_MODULES and module_base not in self.allowed_modules:
                self.violations.append(
                    SecurityViolation(
                        line=node.lineno,
                        column=node.col_offset,
                        rule="BLOCKED_IMPORT",
                        message=f"Forbidden module import from '{node.module}'",
                    )
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Check direct function calls (e.g. eval(), exec())
        if isinstance(node.func, ast.Name):
            if node.func.id in self.BLOCKED_FUNCTIONS:
                self.violations.append(
                    SecurityViolation(
                        line=node.lineno,
                        column=node.col_offset,
                        rule="DANGEROUS_CALL",
                        message=f"Forbidden built-in function call: '{node.func.id}()'",
                    )
                )
        # Check attribute calls (e.g. os.system())
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in {"system", "popen", "spawn", "execve"}:
                self.violations.append(
                    SecurityViolation(
                        line=node.lineno,
                        column=node.col_offset,
                        rule="SYSTEM_EXECUTION",
                        message=f"Forbidden process execution call: '.{node.func.attr}()'",
                        severity="CRITICAL",
                    )
                )
        self.generic_visit(node)


def scan_python_code(code: str, allowed_modules: Optional[Set[str]] = None) -> ScanReport:
    """Scan Python source code and return security audit report.

    Args:
        code: Python source code string.
        allowed_modules: Optional set of modules explicitly allowed.

    Returns:
        ScanReport with is_safe boolean and list of violations.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ScanReport(
            is_safe=False,
            violations=[
                SecurityViolation(
                    line=e.lineno or 1,
                    column=e.offset or 0,
                    rule="SYNTAX_ERROR",
                    message=f"Syntax error in skill code: {e.msg}",
                    severity="CRITICAL",
                )
            ],
        )

    scanner = ASTSecurityScanner(allowed_modules=allowed_modules)
    scanner.visit(tree)

    return ScanReport(
        is_safe=len(scanner.violations) == 0,
        violations=scanner.violations,
    )
