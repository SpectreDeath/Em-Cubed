"""
Language Server Protocol implementation for SKILL.md files in Em-Cubed.
Provides autocomplete, validation, and linting for SKILL.md files.

Compatible with pygls >= 1.0  (uses lsprotocol.types + decorator registration).
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    # Capabilities
    CompletionOptions,
    # Completion
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    # Diagnostics
    Diagnostic,
    DiagnosticSeverity,
    # Document lifecycle
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    # Primitives
    Position,
    Range,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain / surface registries — kept in sync with skills/manifest.yaml
# ---------------------------------------------------------------------------

VALID_DOMAINS = [
    "ANALYTICS",
    "AUTOMATION",
    "CLINICAL_TRIALS",
    "DATA_PROCESSING",
    "DECISION_MAKING",
    "DISTRIBUTED_SYSTEMS",
    "ENSEMBLE",
    "EPIDEMIOLOGY",
    "FEATURE_ENGINEERING",
    "FORENSIC_ECONOMICS",
    "General",
    "GRAPH_ML",
    "KNOWLEDGE_GRAPH",
    "LLM_PROCESSING",
    "MACHINE_LEARNING",
    "META_SKILLS",
    "ML_OPERATIONS",
    "MODEL_VALIDATION",
    "NLP",
    "OPTIMIZATION",
    "RECOMMENDER_SYSTEMS",
    "RESOURCE_MANAGEMENT",
    "SIMULATION",
    "STATISTICS",
    "TECHNICAL_ANALYSIS",
    "TIME_SERIES",
]

COMMON_SURFACES = [
    "python",
    "prolog",
    "hy",
    "z3",
    "datalog",
    "sqlite",
    "quickjs",
    "kanren",
    "clingo",
]


# ---------------------------------------------------------------------------
# SKILL.md frontmatter field schema
# ---------------------------------------------------------------------------

@dataclass
class SkillField:
    """Represents a field in a SKILL.md frontmatter block."""
    name: str
    description: str
    required: bool = False
    type: str = "string"


SKILL_FIELDS: Dict[str, SkillField] = {
    "name":        SkillField("name",        "The name of the skill",               required=True,  type="string"),
    "domain":      SkillField("domain",      "The domain/category of the skill",    required=True,  type="string"),
    "version":     SkillField("version",     "Version of the skill (semver)",        required=False, type="string"),
    "surfaces":    SkillField("surfaces",    "List of execution surfaces",           required=True,  type="list"),
    "triggers":    SkillField("triggers",    "List of trigger words/phrases",        required=False, type="list"),
    "description": SkillField("description", "Brief description of the skill",      required=False, type="string"),
}


# ---------------------------------------------------------------------------
# Language Server
# ---------------------------------------------------------------------------

server = LanguageServer("skill-lsp", "0.2.0")

# In-memory document store: uri -> full text
_documents: Dict[str, str] = {}


# -- Helpers -----------------------------------------------------------------

def _is_in_frontmatter(document: str, position: Position) -> bool:
    lines = document.split("\n")
    if position.line >= len(lines):
        return False
    fm_start = fm_end = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if fm_start == -1:
                fm_start = i
            else:
                fm_end = i
                break
    return fm_start != -1 and fm_end != -1 and fm_start < position.line < fm_end


def _is_in_surfaces_list(document: str, position: Position) -> bool:
    lines = document.split("\n")
    for i in range(position.line, -1, -1):
        if i >= len(lines):
            continue
        line = lines[i]
        if "surfaces:" in line:
            return True
        if line.strip() and not line.strip().startswith("-") and ":" in line:
            break
    return False


def _get_field_name_at_position(before_cursor: str) -> Optional[str]:
    parts = before_cursor.rstrip().split()
    if not parts:
        return None
    last = parts[-1]
    if last.endswith(":"):
        return last[:-1]
    if ":" in last:
        return last.split(":")[0]
    return None


def _frontmatter_completions(before_cursor: str) -> List[CompletionItem]:
    items: List[CompletionItem] = []
    stripped = before_cursor.rstrip()

    # Top-level field name suggestions
    if not stripped or stripped.endswith(":") or stripped == "":
        for field_name, field_info in SKILL_FIELDS.items():
            items.append(CompletionItem(
                label=field_name,
                kind=CompletionItemKind.Property,
                detail=field_info.description,
                documentation=field_info.description,
                insert_text=f"{field_name}: " if not stripped.endswith(":") else "",
            ))
    elif ":" in before_cursor and not before_cursor.strip().startswith("-"):
        fname = _get_field_name_at_position(before_cursor)
        if fname == "surfaces":
            for surface in COMMON_SURFACES:
                items.append(CompletionItem(
                    label=surface,
                    kind=CompletionItemKind.Value,
                    detail=f"Execution surface: {surface}",
                    insert_text=surface,
                ))
        elif fname == "domain":
            for domain in VALID_DOMAINS:
                items.append(CompletionItem(
                    label=domain,
                    kind=CompletionItemKind.Value,
                    detail=f"Skill domain: {domain}",
                    insert_text=domain,
                ))
        elif fname and fname in SKILL_FIELDS and SKILL_FIELDS[fname].type == "list":
            items.append(CompletionItem(
                label="- ",
                kind=CompletionItemKind.Snippet,
                detail="Add list item",
                insert_text="- ",
            ))
    return items


def _list_item_completions() -> List[CompletionItem]:
    return [
        CompletionItem(
            label=surface,
            kind=CompletionItemKind.Value,
            detail=f"Execution surface: {surface}",
            insert_text=surface,
        )
        for surface in COMMON_SURFACES
    ]


def _validate_frontmatter(document: str) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []
    lines = document.split("\n")

    fm_start = fm_end = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if fm_start == -1:
                fm_start = i
            else:
                fm_end = i
                break

    if fm_start == -1 or fm_end == -1:
        diagnostics.append(Diagnostic(
            range=Range(start=Position(line=0, character=0),
                        end=Position(line=0, character=0)),
            message="Missing or malformed frontmatter. Expected --- at start and end.",
            severity=DiagnosticSeverity.Error,
            source="skill-lsp",
        ))
        return diagnostics

    fm_lines = lines[fm_start + 1:fm_end]
    fm_text = "\n".join(fm_lines)

    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        diagnostics.append(Diagnostic(
            range=Range(start=Position(line=fm_start + 1, character=0),
                        end=Position(line=fm_end, character=0)),
            message=f"Invalid YAML in frontmatter: {exc}",
            severity=DiagnosticSeverity.Error,
            source="skill-lsp",
        ))
        return diagnostics

    if not isinstance(data, dict):
        diagnostics.append(Diagnostic(
            range=Range(start=Position(line=fm_start + 1, character=0),
                        end=Position(line=fm_end, character=0)),
            message="Frontmatter must be a YAML mapping (key-value pairs).",
            severity=DiagnosticSeverity.Error,
            source="skill-lsp",
        ))
        return diagnostics

    # Required field checks
    for field_name, field_info in SKILL_FIELDS.items():
        if field_info.required and field_name not in data:
            diagnostics.append(Diagnostic(
                range=Range(start=Position(line=fm_start + 1, character=0),
                            end=Position(line=fm_end, character=0)),
                message=f"Missing required field: '{field_name}'.",
                severity=DiagnosticSeverity.Error,
                source="skill-lsp",
            ))

    # Type checks
    for field_name, value in data.items():
        if field_name not in SKILL_FIELDS:
            continue
        expected = SKILL_FIELDS[field_name].type
        if expected == "string" and not isinstance(value, str):
            diagnostics.append(Diagnostic(
                range=_find_field_range(fm_lines, field_name),
                message=f"Field '{field_name}' must be a string.",
                severity=DiagnosticSeverity.Warning,
                source="skill-lsp",
            ))
        elif expected == "list" and not isinstance(value, list):
            diagnostics.append(Diagnostic(
                range=_find_field_range(fm_lines, field_name),
                message=f"Field '{field_name}' must be a list.",
                severity=DiagnosticSeverity.Warning,
                source="skill-lsp",
            ))

    # Domain validation
    if "domain" in data and isinstance(data["domain"], str):
        if data["domain"] not in VALID_DOMAINS:
            diagnostics.append(Diagnostic(
                range=_find_field_range(fm_lines, "domain"),
                message=f"Unknown domain '{data['domain']}'. "
                        f"Valid: {', '.join(VALID_DOMAINS)}",
                severity=DiagnosticSeverity.Warning,
                source="skill-lsp",
            ))

    # Surface validation
    if "surfaces" in data and isinstance(data["surfaces"], list):
        for surf in data["surfaces"]:
            if surf not in COMMON_SURFACES:
                diagnostics.append(Diagnostic(
                    range=_find_field_range(fm_lines, "surfaces"),
                    message=f"Unknown surface '{surf}'. "
                            f"Valid: {', '.join(COMMON_SURFACES)}",
                    severity=DiagnosticSeverity.Warning,
                    source="skill-lsp",
                ))

    return diagnostics


def _find_field_range(fm_lines: List[str], field_name: str) -> Range:
    for i, line in enumerate(fm_lines):
        if line.strip().startswith(f"{field_name}:"):
            indent = len(line) - len(line.lstrip())
            return Range(
                start=Position(line=i, character=indent),
                end=Position(line=i, character=len(line)),
            )
    return Range(start=Position(line=0, character=0), end=Position(line=0, character=0))


def _publish_diagnostics(uri: str) -> None:
    document = _documents.get(uri, "")
    diags = _validate_frontmatter(document)
    server.publish_diagnostics(uri, diags)


# ---------------------------------------------------------------------------
# LSP feature handlers  (pygls >= 1.0 decorator pattern)
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(params: DidOpenTextDocumentParams) -> None:
    logger.info("Document opened: %s", params.text_document.uri)
    _documents[params.text_document.uri] = params.text_document.text
    _publish_diagnostics(params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: DidChangeTextDocumentParams) -> None:
    logger.info("Document changed: %s", params.text_document.uri)
    if params.content_changes:
        _documents[params.text_document.uri] = params.content_changes[-1].text
    _publish_diagnostics(params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(params: DidSaveTextDocumentParams) -> None:
    logger.info("Document saved: %s", params.text_document.uri)
    _publish_diagnostics(params.text_document.uri)


@server.feature(
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(trigger_characters=[":", "-", " ", "\n"]),
)
def completion(params: CompletionParams) -> CompletionList:
    uri = params.text_document.uri
    document = _documents.get(uri, "")
    position = params.position

    lines = document.split("\n")
    if position.line >= len(lines):
        return CompletionList(is_incomplete=False, items=[])

    line = lines[position.line]
    before_cursor = line[: position.character]
    items: List[CompletionItem] = []

    if _is_in_frontmatter(document, position):
        items.extend(_frontmatter_completions(before_cursor))
    elif before_cursor.strip().startswith("- ") and _is_in_surfaces_list(document, position):
        items.extend(_list_item_completions())
    elif before_cursor.endswith(":"):
        fname = _get_field_name_at_position(before_cursor)
        if fname == "surfaces":
            items.extend(_list_item_completions())
        elif fname == "domain":
            items.extend([
                CompletionItem(label=d, kind=CompletionItemKind.Value, insert_text=d)
                for d in VALID_DOMAINS
            ])

    return CompletionList(is_incomplete=False, items=items)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("Starting Em-Cubed Skill Language Server (pygls >= 1.0)...")
    server.start_io()


if __name__ == "__main__":
    main()