"""
Language Server Protocol implementation for SKILL.md files in Em-Cubed.
Provides autocomplete, validation, and linting for SKILL.md files.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml

from pygls.lsp import LanguageServer
from pygls.lsp.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    TextDocumentIdentifier,
    TextDocumentItem,
    TextDocumentPositionParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    InitializeResult,
    InitializeParams,
    ServerCapabilities,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SkillField:
    """Represents a field in a SKILL.md file."""
    name: str
    description: str
    required: bool = False
    type: str = "string"

# Define expected fields in SKILL.md frontmatter
SKILL_FIELDS = {
    "name": SkillField("name", "The name of the skill", required=True, type="string"),
    "domain": SkillField("domain", "The domain/category of the skill", required=True, type="string"),
    "version": SkillField("version", "Version of the skill (semver)", required=False, type="string"),
    "surfaces": SkillField("surfaces", "List of execution surfaces", required=True, type="list"),
    "triggers": SkillField("triggers", "List of trigger words/phrases", required=False, type="list"),
    "description": SkillField("description", "Brief description of the skill", required=False, type="string"),
}

# Common surface types
COMMON_SURFACES = [
    "python",
    "prolog", 
    "hy",
    "z3",
    "datalog",
    "sqlite",
    "quickjs",
    "cangjie"
]

class SkillLanguageServer(LanguageServer):
    """Language Server for SKILL.md files."""
    
    def __init__(self):
        super().__init__("skill-lsp", "0.1.0")
        self.documents: Dict[str, str] = {}
        
    def initialize(self, params: InitializeParams):
        """Initialize the language server."""
        logger.info("Initializing Skill Language Server")
        return InitializeResult(
            capabilities=ServerCapabilities(
                text_document_sync=TextDocumentSyncKind.Incremental,
                completion_provider=self._get_completion_options(),
                document_formatting=False,
                document_range_formatting=False,
                document_highlight=False,
                document_symbol=False,
                workspace_symbol=False,
                code_action_provider=False,
                code_lens_provider=False,
                document_link_provider=False,
                color_provider=False,
                folding_range_provider=False,
                execute_command_provider=False,
                selection_range_provider=False,
                linked_editing_range_provider=False,
                call_hierarchy_provider=False,
                semantic_tokens_provider=False,
                moniker_provider=False,
                type_hierarchy_provider=False,
                inline_value_provider=False,
                inlay_hint_provider=False,
                diagnostic_provider=self._get_diagnostic_options(),
            )
        )
    
    def _get_completion_options(self):
        """Get completion provider options."""
        return {
            "resolve_provider": False,
            "trigger_characters": [":", "-", " ", "\n"],
        }
    
    def _get_diagnostic_options(self):
        """Get diagnostic provider options."""
        return {
            "inter_file_dependencies": False,
            "workspace_diagnostics": False,
        }
    
    def text_document_did_open(self, params: DidOpenTextDocumentParams):
        """Handle document open event."""
        logger.info(f"Document opened: {params.text_document.uri}")
        self.documents[params.text_document.uri] = params.text_document.text
        self._validate_document(params.text_document.uri)
    
    def text_document_did_change(self, params: DidChangeTextDocumentParams):
        """Handle document change event."""
        logger.info(f"Document changed: {params.text_document.uri}")
        self.documents[params.text_document.uri] = params.content_changes[-1].text
        self._validate_document(params.text_document.uri)
    
    def text_document_did_save(self, params: DidSaveTextDocumentParams):
        """Handle document save event."""
        logger.info(f"Document saved: {params.text_document.uri}")
        self._validate_document(params.text_document.uri)
    
    def text_document_completion(self, params: TextDocumentPositionParams):
        """Handle completion requests."""
        uri = params.text_document.uri
        if uri not in self.documents:
            return CompletionList(is_incomplete=False, items=[])
            
        document = self.documents[uri]
        position = params.position
        
        # Get line content up to cursor position
        lines = document.split('\n')
        if position.line >= len(lines):
            return CompletionList(is_incomplete=False, items=[])
            
        line = lines[position.line]
        before_cursor = line[:position.character]
        
        # Determine completion context
        completions = []
        
        # If we're in the frontmatter (between --- lines)
        if self._is_in_frontmatter(document, position):
            completions.extend(self._get_frontmatter_completions(before_cursor, position))
        elif before_cursor.strip().startswith("- ") and self._is_in_list(document, position):
            # Inside a YAML list
            completions.extend(self._get_list_item_completions(before_cursor, position))
        elif before_cursor.endswith(":"):
            # After a colon, suggest values
            completions.extend(self._get_value_completions(before_cursor, position, document))
        
        return CompletionList(is_incomplete=False, items=completions)
    
    def _is_in_frontmatter(self, document: str, position: Position) -> bool:
        """Check if position is inside the YAML frontmatter."""
        lines = document.split('\n')
        if position.line >= len(lines):
            return False
            
        # Find frontmatter boundaries
        frontmatter_start = -1
        frontmatter_end = -1
        
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if frontmatter_start == -1:
                    frontmatter_start = i
                else:
                    frontmatter_end = i
                    break
        
        return frontmatter_start != -1 and frontmatter_end != -1 and frontmatter_start < position.line < frontmatter_end
    
    def _get_frontmatter_completions(self, before_cursor: str, position: Position) -> List[CompletionItem]:
        """Get completions for frontmatter fields."""
        completions = []
        
        # If we're at the start of a line or after whitespace, suggest field names
        stripped = before_cursor.rstrip()
        if not stripped or stripped.endswith(":") or stripped.endswith("- ") or stripped == "":
            # Suggest field names
            for field_name, field_info in SKILL_FIELDS.items():
                # Don't suggest already present fields (simple check)
                if f"{field_name}:" not in before_cursor:
                    completions.append(CompletionItem(
                        label=field_name,
                        kind=CompletionItemKind.Property,
                        detail=field_info.description,
                        documentation=field_info.description,
                        insert_text=f"{field_name}: " if not stripped.endswith(":") else "",
                        insert_text_format=2  # PlainText
                    ))
        
        # If we're typing a field value
        elif ":" in before_cursor and not before_cursor.strip().startswith("-"):
            field_part = before_cursor.split(":")[0].strip()
            if field_name := self._get_field_name_at_position(before_cursor):
                if field_name in SKILL_FIELDS:
                    field_info = SKILL_FIELDS[field_name]
                    if field_info.type == "list":
                        # Suggest list item start
                        completions.append(CompletionItem(
                            label="- ",
                            kind=CompletionItemKind.Snippet,
                            detail="Add list item",
                            documentation="Start a new list item",
                            insert_text="- ",
                            insert_text_format=2
                        ))
                    elif field_name == "surfaces":
                        # Suggest surface types
                        for surface in COMMON_SURFACES:
                            completions.append(CompletionItem(
                                label=surface,
                                kind=CompletionItemKind.Value,
                                detail=f"Execution surface: {surface}",
                                documentation=f"Use the {surface} execution surface",
                                insert_text=surface,
                                insert_text_format=2
                            ))
        
        return completions
    
    def _get_list_item_completions(self, before_cursor: str, position: Position) -> List[CompletionItem]:
        """Get completions for list items."""
        completions = []
        
        # Determine what kind of list we're in
        if self._is_in_surfaces_list(before_cursor, position):
            for surface in COMMON_SURFACES:
                completions.append(CompletionItem(
                    label=surface,
                    kind=CompletionItemKind.Value,
                    detail=f"Execution surface: {surface}",
                    documentation=f"Use the {surface} execution surface",
                    insert_text=surface,
                    insert_text_format=2
                ))
        
        return completions
    
    def _is_in_surfaces_list(self, before_cursor: str, position: Position) -> bool:
        """Check if we're inside the surfaces list."""
        # Simple heuristic: if we've seen "surfaces:" recently
        lines = before_cursor.split('\n')
        for line in reversed(lines):
            if "surfaces:" in line:
                return True
            if line.strip() and not line.strip().startswith("-") and ":" in line:
                # We've moved past the surfaces list
                break
        return False
    
    def _get_value_completions(self, before_cursor: str, position: Position, document: str) -> List[CompletionItem]:
        """Get completions for values after a colon."""
        completions = []
        
        # Get the field name
        lines = document.split('\n')
        if position.line < len(lines):
            line = lines[position.line]
            if ':' in line:
                field_name = line.split(':')[0].strip()
                if field_name in SKILL_FIELDS:
                    field_info = SKILL_FIELDS[field_name]
                    if field_info.type == "list" and field_name == "surfaces":
                        for surface in COMMON_SURFACES:
                            completions.append(CompletionItem(
                                label=surface,
                                kind=CompletionItemKind.Value,
                                detail=f"Execution surface: {surface}",
                                documentation=f"Use the {surface} execution surface",
                                insert_text=surface,
                                insert_text_format=2
                            ))
        
        return completions
    
    def _get_field_name_at_position(self, before_cursor: str) -> Optional[str]:
        """Extract field name from text before cursor."""
        # Find the last word before colon
        parts = before_cursor.rstrip().split()
        if not parts:
            return None
            
        last_part = parts[-1]
        if last_part.endswith(":"):
            return last_part[:-1]
        elif ":" in last_part:
            return last_part.split(":")[0]
        
        return None
    
    def _validate_document(self, uri: str):
        """Validate the document and publish diagnostics."""
        if uri not in self.documents:
            return
            
        document = self.documents[uri]
        diagnostics = []
        
        # Validate frontmatter
        frontmatter_diagnostics = self._validate_frontmatter(document)
        diagnostics.extend(frontmatter_diagnostics)
        
        # Publish diagnostics
        self.publish_diagnostics(uri, frontmatter_diagnostics)
    
    def _validate_frontmatter(self, document: str) -> List[Diagnostic]:
        """Validate the YAML frontmatter."""
        diagnostics = []
        lines = document.split('\n')
        
        # Find frontmatter boundaries
        frontmatter_start = -1
        frontmatter_end = -1
        
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if frontmatter_start == -1:
                    frontmatter_start = i
                else:
                    frontmatter_end = i
                    break
        
        if frontmatter_start == -1 or frontmatter_end == -1:
            # No proper frontmatter
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=0)
                ),
                message="Missing or malformed frontmatter. Expected --- at start and end of frontmatter.",
                severity=DiagnosticSeverity.Error,
                source="skill-lsp"
            ))
            return diagnostics
        
        # Extract frontmatter content
        frontmatter_lines = lines[frontmatter_start + 1:frontmatter_end]
        frontmatter_text = '\n'.join(frontmatter_lines)
        
        try:
            data = yaml.safe_load(frontmatter_text)
            if not isinstance(data, dict):
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=frontmatter_start + 1, character=0),
                        end=Position(line=frontmatter_end, character=0)
                    ),
                    message="Frontmatter must be a YAML mapping (key-value pairs)",
                    severity=DiagnosticSeverity.Error,
                    source="skill-lsp"
                ))
                return diagnostics
            
            # Check required fields
            for field_name, field_info in SKILL_FIELDS.items():
                if field_info.required and field_name not in data:
                    # Find approximate line for the field
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=frontmatter_start + 1, character=0),
                            end=Position(line=frontmatter_end, character=0)
                        ),
                        message=f"Missing required field: {field_name}",
                        severity=DiagnosticSeverity.Error,
                        source="skill-lsp"
                    ))
            
            # Validate field types
            for field_name, value in data.items():
                if field_name in SKILL_FIELDS:
                    expected_type = SKILL_FIELDS[field_name].type
                    if expected_type == "string" and not isinstance(value, str):
                        diagnostics.append(Diagnostic(
                            range=self._find_field_range(frontmatter_lines, field_name),
                            message=f"Field '{field_name}' must be a string",
                            severity=DiagnosticSeverity.Warning,
                            source="skill-lsp"
                        ))
                    elif expected_type == "list" and not isinstance(value, list):
                        diagnostics.append(Diagnostic(
                            range=self._find_field_range(frontmatter_lines, field_name),
                            message=f"Field '{field_name}' must be a list",
                            severity=DiagnosticSeverity.Warning,
                            source="skill-lsp"
                        ))
                        
        except yaml.YAMLError as e:
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=frontmatter_start + 1, character=0),
                    end=Position(line=frontmatter_end, character=0)
                ),
                message=f"Invalid YAML in frontmatter: {str(e)}",
                severity=DiagnosticSeverity.Error,
                source="skill-lsp"
            ))
        
        return diagnostics
    
    def _find_field_range(self, lines: List[str], field_name: str) -> Range:
        """Find the range of a field in the frontmatter lines."""
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{field_name}:"):
                return Range(
                    start=Position(line=i, character=len(line) - len(line.lstrip())),
                    end=Position(line=i, character=len(line))
                )
        return Range(start=Position(line=0, character=0), end=Position(line=0, character=0))

def main():
    """Run the language server."""
    logger.info("Starting Skill Language Server...")
    server = SkillLanguageServer()
    server.start_io()

if __name__ == "__main__":
    main()