import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()

__all__ = ["search_registry", "get_search_index", "WhooshSearchIndex", "SearchIndexManager"]


class SearchIndexManager:
    """Manages Whoosh search index with proper state isolation."""

    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or Path(".whoosh_index")
        self._index_hash: Optional[str] = None
        self._whoosh_index: Optional[WhooshSearchIndex] = None


class WhooshSearchIndex:
    """Whoosh-based full-text search index for skills."""

    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or Path(".whoosh_index")
        self.index_dir.mkdir(exist_ok=True)
        self.ix = None
        self._init_index()

    def _init_index(self):
        """Initialize or open the Whoosh index."""
        try:
            from whoosh import index
            from whoosh.fields import Schema, TEXT, KEYWORD, ID

            schema = Schema(
                name=TEXT(stored=True, field_boost=2.0),
                description=TEXT(stored=True),
                tags=KEYWORD(stored=True, commas=True),
                surface=KEYWORD(stored=True),
                content=TEXT(stored=True),
                path=ID(stored=True, unique=True),
            )

            if index.exists_in(str(self.index_dir)):
                self.ix = index.open_dir(str(self.index_dir))
                # Check if schema matches
                if not self.ix.schema == schema:
                    logger.warning("Schema mismatch, recreating index")
                    self.ix = None

            if self.ix is None:
                self.ix = index.create_in(str(self.index_dir), schema)

        except ImportError:
            logger.warning("Whoosh not available, falling back to naive search")
            self.ix = None

    def index_skills(self, registry: List[Dict[str, Any]]):
        """Index skills from registry."""
        if not self.ix:
            return

        writer = self.ix.writer()
        try:
            for skill in registry:
                # Combine all searchable content
                content_parts = [
                    skill.get("name", ""),
                    skill.get("purpose", ""),
                    skill.get("description", ""),
                    skill.get("domain", ""),
                ]

                # Add tags
                logic_tags = skill.get("logic_tags", [])
                heuristic_tags = skill.get("heuristic_tags", [])
                all_tags = logic_tags + heuristic_tags

                # Add surfaces
                surfaces = skill.get("surfaces", [])

                content = " ".join(content_parts)
                tags = ",".join(all_tags)
                surface = ",".join(surfaces)

                writer.update_document(
                    name=skill.get("name", ""),
                    description=skill.get("description", ""),
                    tags=tags,
                    surface=surface,
                    content=content,
                    path=skill.get("path", ""),
                )

            writer.commit()
            logger.info("Whoosh index updated", skills_count=len(registry))

        except Exception as e:
            logger.exception("Failed to index skills", error=str(e))
            writer.cancel()

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search the index with enhanced scoring."""
        if not self.ix:
            return []

        try:
            from whoosh import qparser, scoring

            # Use BM25 scoring with fuzzy matching
            searcher = self.ix.searcher(weighting=scoring.BM25F())

            # Parse query with fuzzy matching for typos
            parser = qparser.MultifieldParser(
                ["name", "description", "content", "tags"],
                self.ix.schema
            )
            parser.add_plugin(qparser.FuzzyTermPlugin())

            # Add fuzzy terms for common typos
            parsed_query = parser.parse(query)

            results = searcher.search(parsed_query, limit=max_results)

            search_results = []
            for hit in results:
                # Calculate enhanced score
                score = hit.score

                # Boost for exact tag matches
                query_lower = query.lower()
                tags = hit.get("tags", "").split(",")
                if any(query_lower in tag.lower() for tag in tags):
                    score *= 1.5

                # Boost for surface matches
                surfaces = hit.get("surface", "").split(",")
                if any(query_lower in surf.lower() for surf in surfaces):
                    score *= 1.2

                search_results.append({
                    "name": hit.get("name"),
                    "description": hit.get("description"),
                    "path": hit.get("path"),
                    "tags": tags,
                    "surfaces": surfaces,
                    "score": score,
                })

            searcher.close()
            return search_results

        except Exception as e:
            logger.exception("Whoosh search failed", error=str(e))
            return []


def get_search_index(index_dir: Optional[Path] = None) -> WhooshSearchIndex:
    """Get or create a search index instance."""
    return WhooshSearchIndex(index_dir)


def _get_registry_hash(registry: List[Dict[str, Any]]) -> str:
    """Get a hash of the registry for change detection."""
    import hashlib
    import json

    # Create a stable representation by sorting keys and items
    stable_json = json.dumps(registry, sort_keys=True, default=str)
    return hashlib.sha256(stable_json.encode()).hexdigest()


def search_registry(query: str, registry_path: Path, max_results: int = 10, use_whoosh: bool = True, index_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Search the skill registry with whoosh or fallback to naive search."""
    logger.info("Searching registry", query=query, registry_path=str(registry_path), max_results=max_results, use_whoosh=use_whoosh)

    query = query.strip()
    if not query:
        return []

    if not registry_path.exists():
        logger.error("Registry file not found", registry_path=str(registry_path))
        return [{"error": "Registry file not found. Run indexer first."}]

    # Load registry
    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        return [{"error": f"Error reading registry: {str(e)}"}]

    # Try whoosh search first if enabled
    if use_whoosh:
        try:
            search_index = get_search_index(index_dir)

            # Check if we need to update the index
            current_hash = _get_registry_hash(registry)
            index_hash_file = index_dir / ".registry_hash" if index_dir else Path(".whoosh_index/.registry_hash")

            # Read existing hash
            existing_hash = None
            if index_hash_file.exists():
                try:
                    existing_hash = index_hash_file.read_text().strip()
                except Exception:
                    existing_hash = None

            if existing_hash != current_hash:
                logger.info("Updating Whoosh index", registry_skills=len(registry))
                search_index.index_skills(registry)
                # Write new hash
                index_hash_file.parent.mkdir(exist_ok=True)
                index_hash_file.write_text(current_hash)
            else:
                logger.debug("Whoosh index is up to date")

            whoosh_results = search_index.search(query, max_results)
            if whoosh_results:
                logger.info("Whoosh search succeeded", results_count=len(whoosh_results))
                return whoosh_results
        except Exception as e:
            logger.warning("Whoosh search failed, falling back to naive search", error=str(e))

    # Fallback to naive search
    return _naive_search_registry(query, registry, max_results)


def _naive_search_registry(query: str, registry: List[Dict[str, Any]], max_results: int = 10) -> List[Dict[str, Any]]:
    """Fallback naive search implementation."""
    logger.info("Using naive search fallback")

    query_lower = query.lower()
    results = []

    for skill in registry:
        score = 0
        name = skill.get("name", "").lower()
        purpose = skill.get("purpose", "").lower()
        description = skill.get("description", "").lower()
        surfaces = [s.lower() for s in skill.get("surfaces", [])]
        logic_tags = [t.lower() for t in skill.get("logic_tags", [])]
        heuristic_tags = [t.lower() for t in skill.get("heuristic_tags", [])]

        if query_lower in name:
            score += 10
        if query_lower in purpose:
            score += 5
        if query_lower in description:
            score += 3
        if query_lower in surfaces:
            score += 6

        # Substring matches for words in query
        for word in query_lower.split():
            if word in name or word in purpose or word in description:
                score += 2
            if word in surfaces:
                score += 4
            if word in logic_tags or word in heuristic_tags:
                score += 8

        if score > 0:
            results.append(
                {
                    "name": skill.get("name"),
                    "domain": skill.get("domain"),
                    "purpose": (purpose[:100] + "...") if purpose else "",
                    "path": skill.get("path"),
                    "surfaces": skill.get("surfaces", []),
                    "logic_tags": skill.get("logic_tags", []),
                    "heuristic_tags": skill.get("heuristic_tags", []),
                    "score": score,
                }
            )

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:max_results]

    logger.info("Naive search completed", total_matches=len(results), returned=len(top_results))
    return top_results



