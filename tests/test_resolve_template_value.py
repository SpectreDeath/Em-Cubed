"""Tests for resolve_template_value and _resolve_path in distributed workflow."""

from em_cubed.workflow.distributed import _resolve_path, resolve_template_value


def test_resolve_path_nested_dict():
    data = {"a": {"b": {"c": 42}}}
    assert _resolve_path(data, "a.b.c") == 42
    assert _resolve_path(data, "a.b") == {"c": 42}
    assert _resolve_path(data, "a.missing") is None


def test_resolve_path_list_index():
    data = {"items": ["zero", "one", "two"]}
    assert _resolve_path(data, "items.1") == "one"
    assert _resolve_path(data, "items.99") is None


def test_resolve_template_value_full_match():
    results = {"task1": {"output": {"val": 100}}}
    tmpl = "{{ tasks.task1.output.val }}"
    assert resolve_template_value(tmpl, results) == 100


def test_resolve_template_value_partial_string():
    results = {"task1": {"status": "success"}}
    tmpl = "Status is {{ tasks.task1.status }}"
    assert resolve_template_value(tmpl, results) == "Status is success"


def test_resolve_template_value_missing_dep():
    results = {"task1": 42}
    tmpl = "{{ tasks.missing_task.result }}"
    assert resolve_template_value(tmpl, results) == tmpl


def test_resolve_template_value_non_string():
    results = {"task1": 42}
    assert resolve_template_value(123, results) == 123
    assert resolve_template_value(True, results) is True
    assert resolve_template_value(None, results) is None


def test_resolve_template_value_nested_dict_and_list():
    results = {"t1": {"res": "ok"}}
    data = {"key1": "{{ tasks.t1.res }}", "key2": ["{{ tasks.t1.res }}", 5]}
    expected = {"key1": "ok", "key2": ["ok", 5]}
    assert resolve_template_value(data, results) == expected
