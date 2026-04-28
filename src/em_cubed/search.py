import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()


def search_registry(query: str, registry_path: Path, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search the skill registry with multi-surface scoring."""
    logger.info("Searching registry", query=query, registry_path=str(registry_path), max_results=max_results)

    query = query.strip().lower()
    results = []

    if not registry_path.exists():
        logger.error("Registry file not found", registry_path=str(registry_path))
        return [{"error": "Registry file not found. Run indexer first."}]

    # Return empty results for empty queries
    if not query:
        return []

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)

        for skill in registry:
            score = 0
            name = skill.get("name", "").lower()
            purpose = skill.get("purpose", "").lower()
            description = skill.get("description", "").lower()
            surfaces = [s.lower() for s in skill.get("surfaces", [])]
            logic_tags = [t.lower() for t in skill.get("logic_tags", [])]
            heuristic_tags = [t.lower() for t in skill.get("heuristic_tags", [])]

            if query in name:
                score += 10
            if query in purpose:
                score += 5
            if query in description:
                score += 3
            if query in surfaces:
                score += 6

            # Substring matches for words in query
            for word in query.split():
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
    except Exception as e:
        return [{"error": f"Error reading registry: {str(e)}"}]

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:max_results]

    logger.info("Search completed", total_matches=len(results), returned=len(top_results))
    return top_results


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m em_cubed.search <registry_path> <query>")
        sys.exit(1)

    registry_path = Path(sys.argv[1])
    query = sys.argv[2]
    matches = search_registry(query, registry_path)
    print(json.dumps(matches, indent=2))


if __name__ == "__main__":
    main()
