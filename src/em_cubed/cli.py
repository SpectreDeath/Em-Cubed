"""Command-line interface for Em-Cubed."""

import argparse
import sys
from pathlib import Path
import structlog

from em_cubed.indexer import reindex
from em_cubed.search import search_registry
from em_cubed.plugin_manager import PluginManager

# Configure structlog for CLI
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Em-Cubed: Multi-Surface Skill Framework",
        prog="em3"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Index command
    index_parser = subparsers.add_parser("index", help="Index skills directory")
    index_parser.add_argument("skills_dir", help="Directory containing SKILL.md files")
    index_parser.add_argument(
        "--output",
        "-o",
        default="registry.json",
        help="Output registry file (default: registry.json)"
    )
    index_parser.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Only re-index changed files (faster for large collections)"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search skill registry")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--registry",
        "-r",
        default="registry.json",
        help="Registry file path (default: registry.json)"
    )
    search_parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Launch FastAPI server")
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind server to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to bind server to (default: 8000)"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute code on specified surface")
    run_parser.add_argument(
        "--surface",
        "-s",
        required=True,
        help="Surface to execute code on"
    )
    run_parser.add_argument(
        "--code",
        "-c",
        required=True,
        help="Code to execute"
    )
    run_parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        help="Maximum execution time in seconds (default: 30)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "index":
            _handle_index(args)
        elif args.command == "search":
            _handle_search(args)
        elif args.command == "serve":
            _handle_serve(args)
        elif args.command == "run":
            _handle_run(args)
    except Exception as e:
        logger.exception("CLI command failed", command=args.command, error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_index(args):
    """Handle index command."""
    skills_dir = Path(args.skills_dir)
    registry_output = Path(args.output)
    incremental = args.incremental

    if not skills_dir.exists():
        raise ValueError(f"Skills directory does not exist: {skills_dir}")

    if incremental:
        logger.info("Incremental indexing skills", skills_dir=str(skills_dir), output=str(registry_output))
        from em_cubed.indexer import reindex_incremental
        reindex_incremental(skills_dir, registry_output)
        print(f"Registry incrementally updated at {registry_output}")
    else:
        logger.info("Full indexing skills", skills_dir=str(skills_dir), output=str(registry_output))
        reindex(skills_dir, registry_output)
        print(f"Registry created at {registry_output}")


def _handle_search(args):
    """Handle search command."""
    registry_path = Path(args.registry)
    query = args.query
    max_results = args.max_results

    logger.info("Searching registry", query=query, registry=str(registry_path))
    results = search_registry(query, registry_path, max_results)

    if results and "error" in results[0]:
        print(f"Error: {results[0]['error']}", file=sys.stderr)
        return

    import json
    print(json.dumps(results, indent=2))


def _handle_serve(args):
    """Handle serve command."""
    host = args.host
    port = args.port

    # Check if uvicorn is available
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn is required for serving. Install with: pip install uvicorn")

    logger.info("Starting FastAPI server", host=host, port=port)
    print(f"Starting server at http://{host}:{port}")

    # Import here to avoid import issues if uvicorn not available
    from api.main import app
    uvicorn.run(app, host=host, port=port)


def _handle_run(args):
    """Handle run command."""
    surface_name = args.surface
    code = args.code
    timeout = args.timeout

    plugin_manager = PluginManager()
    surface = plugin_manager.get(surface_name)

    if not surface:
        available_surfaces = plugin_manager.get_available_surfaces()
        raise ValueError(f"Surface '{surface_name}' not found. Available: {', '.join(available_surfaces)}")

    if not surface.available:
        raise ValueError(f"Surface '{surface_name}' is not available")

    logger.info("Executing code", surface=surface_name, code_length=len(code), timeout=timeout)

    import asyncio
    import json

    async def run_async():
        result = await surface.execute(code)
        print(json.dumps(result, indent=2))

    asyncio.run(run_async())


if __name__ == "__main__":
    main()