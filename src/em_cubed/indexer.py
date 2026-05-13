"""Skill indexing and reindexing utilities.

Provides functions to scan skill directories, extract metadata from SKILL.md files,
and build/incrementally update the skill registry JSON.
"""

import json
import os
import re
from pathlib import Path
import yaml  # type: ignore
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()

__all__ = ["reindex", "get_skill_metadata", "reindex_incremental"]


def extract_fenced_block(content: str, lang: str) -> Optional[str]:
    """Extract first fenced code block of a given language tag."""
    pattern = rf"`+{lang}\s*\r?\n(.*?)`+"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_prolog_tags(prolog_source: Optional[str]) -> List[str]:
    """Extract predicate names from Prolog clause heads as logic_tags."""
    if not prolog_source:
        return []
    import re
    # Match predicate heads: name( or name :-
    # Don't anchor to line start - allows finding predicates with indentation
    heads = re.findall(r"([a-z][a-zA-Z0-9_]*)\s*[:(]", prolog_source)
    # Deduplicate, exclude Prolog builtins
    builtins = {"not", "is", "true", "fail", "assert", "retract"}
    return list(dict.fromkeys(h for h in heads if h not in builtins))


def extract_hy_tags(hy_source: Optional[str]) -> List[str]:
    """Extract function names from Hy defn forms as heuristic_tags."""
    if not hy_source:
        return []
    fns = re.findall(r"\(defn\s+([a-zA-Z][a-zA-Z0-9_\-?!]*)", hy_source)  # cspell:ignore defn
    return list(dict.fromkeys(fns))


def get_skill_metadata(file_path: Path, skills_dir: Path) -> Optional[Dict[str, Any]]:
    """Extract extended metadata from a SKILL.md file."""
    try:
        with open(file_path, encoding="utf-8-sig") as f:
            content = f.read()

        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        fm = yaml.safe_load(parts[1]) or {}
        body = parts[2]

        # Use new SkillMetadata class for full extraction
        from .skills.metadata import SkillMetadata
        metadata = SkillMetadata.from_frontmatter(fm, body, file_path)
        result = metadata.to_registry_dict()

        # Extract separate tags for backward compatibility with search module
        prolog_source = extract_fenced_block(body, "prolog")
        hy_source = extract_fenced_block(body, "hy")
        python_source = extract_fenced_block(body, "python")

        logic_tags = extract_prolog_tags(prolog_source)
        heuristic_tags = extract_hy_tags(hy_source)
        if python_source:
            try:
                from .surfaces.python_surface import PythonSurface
                heuristic_tags.extend(PythonSurface.extract_tags(python_source))
            except ImportError:
                pass
        
        # Add Cangjie support
        cj_source = extract_fenced_block(body, "cangjie") or extract_fenced_block(body, "cj")
        if cj_source:
            try:
                from .surfaces.cangjie_surface import CangjieSurface
                heuristic_tags.extend(CangjieSurface.extract_tags(cj_source))
            except ImportError:
                pass

        result["logic_tags"] = logic_tags
        result["heuristic_tags"] = heuristic_tags
        result["last_modified"] = os.path.getmtime(file_path)
        result["path"] = str(file_path.resolve())

        # Default surfaces to python if none detected
        if not result["surfaces"]:
            result["surfaces"] = ["python"]

        # Ensure "tags" includes all tags
        all_tags = list(set(logic_tags + heuristic_tags + result.get("tags", [])))
        result["tags"] = all_tags

        return result

    except Exception as e:
        logger.warning("Error indexing skill file", path=str(file_path), error=str(e))
        return None


def reindex_incremental(skills_dir: Path, registry_output: Path) -> None:
    """Update only changed skills in the registry."""
    logger.info("Starting incremental skill reindex", skills_dir=str(skills_dir), registry_output=str(registry_output))

    # Load existing registry
    existing_registry = []
    if registry_output.exists():
        try:
            with open(registry_output, encoding="utf-8-sig") as f:
                existing_registry = json.load(f)
        except Exception as e:
            logger.warning("Could not load existing registry, starting fresh", error=str(e))
            existing_registry = []

    # Build lookup by path for existing skills
    existing_by_path = {skill["path"]: skill for skill in existing_registry}

    updated_registry = []
    processed_paths = set()

    # Check all skill files
    for skill_file in _discover_skill_files(skills_dir):
        rel_path = str(skill_file.relative_to(skills_dir.parent))
        processed_paths.add(rel_path)

        # Check if file has changed
        current_mtime = os.path.getmtime(skill_file)
        existing_skill = existing_by_path.get(rel_path)

        if existing_skill and existing_skill.get("last_modified") == current_mtime:
            # File unchanged, keep existing metadata
            updated_registry.append(existing_skill)
            logger.debug("Skill unchanged, keeping cached metadata", path=rel_path)
        else:
            # File changed or new, re-index
            metadata = get_skill_metadata(skill_file, skills_dir)
            if metadata:
                updated_registry.append(metadata)
                if existing_skill:
                    logger.debug("Skill updated", path=rel_path)
                else:
                    logger.debug("New skill added", path=rel_path)

    # Remove skills for deleted files
    removed_count = 0
    for existing_path in existing_by_path:
        if existing_path not in processed_paths:
            logger.debug("Skill removed (file deleted)", path=existing_path)
            removed_count += 1

    # Sort registry for consistent output
    updated_registry.sort(key=lambda x: x["path"])

    with open(registry_output, "w", encoding="utf-8") as f:
        json.dump(updated_registry, f, indent=2)

    multi = [s for s in updated_registry if len(s.get("surfaces", [])) > 1]
    logger.info(
        "Incremental reindex completed",
        total_skills=len(updated_registry),
        multi_surface=len(multi),
        single_surface=len(updated_registry) - len(multi),
        updated=len(updated_registry) - len(existing_registry) + removed_count,
        removed=removed_count,
        registry_path=str(registry_output),
    )


def reindex(skills_dir: Path, registry_output: Path) -> None:
    """Reindex all skills in the given directory and write registry."""
    logger.info("Starting full skill reindex", skills_dir=str(skills_dir), registry_output=str(registry_output))

    registry = []

    # Look for both SKILL.md and SKILL_*.md files
    for skill_file in _discover_skill_files(skills_dir):
        metadata = get_skill_metadata(skill_file, skills_dir)
        if metadata:
            registry.append(metadata)

    with open(registry_output, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    multi = [s for s in registry if len(s.get("surfaces", [])) > 1]
    logger.info(
        "Full skill reindex completed",
        total_skills=len(registry),
        multi_surface=len(multi),
        single_surface=len(registry) - len(multi),
        registry_path=str(registry_output),
    )


def _discover_skill_files(skills_dir: Path) -> List[Path]:
    """Discover all skill files in the directory."""
    skill_files = []

    # Look for both SKILL.md and SKILL_*.md files
    for skill_file in skills_dir.glob("**/SKILL.md"):
        skill_files.append(skill_file)

    for skill_file in skills_dir.glob("**/SKILL_*.md"):
        skill_files.append(skill_file)

    return skill_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m em_cubed.indexer <skills_dir> <registry_output>")
        sys.exit(1)

    skills_dir = Path(sys.argv[1])
    registry_output = Path(sys.argv[2])
    reindex(skills_dir, registry_output)
