"""Unit tests for Em-Cubed AST security scanner."""

from __future__ import annotations

from em_cubed.security.ast_scanner import scan_python_code


def test_safe_python_code():
    code = """
def add(a: int, b: int) -> int:
    return a + b
    """
    report = scan_python_code(code)
    assert report.is_safe is True
    assert len(report.violations) == 0


def test_blocked_module_import():
    code = """
import os
import sys

def run():
    print(os.getcwd())
    """
    report = scan_python_code(code)
    assert report.is_safe is False
    assert len(report.violations) >= 1
    rules = [v.rule for v in report.violations]
    assert "BLOCKED_IMPORT" in rules


def test_dangerous_function_eval():
    code = """
def execute_dynamic(user_input):
    return eval(user_input)
    """
    report = scan_python_code(code)
    assert report.is_safe is False
    assert len(report.violations) == 1
    assert report.violations[0].rule == "DANGEROUS_CALL"


def test_syntax_error_handling():
    code = "def broken_func("
    report = scan_python_code(code)
    assert report.is_safe is False
    assert report.violations[0].rule == "SYNTAX_ERROR"
