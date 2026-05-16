"""Command-line interface for Em-Cubed."""

import argparse
import sys
from pathlib import Path
import structlog
import asyncio
import json

from em_cubed.indexer import reindex, get_skill_metadata
from em_cubed.search import search_registry
from em_cubed.plugin_manager import PluginManager

__all__ = ["main"]

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
    run_parser.add_argument(
        "--trace",
        action="store_true",
        help="Show hierarchical execution trace after run"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate all skills")
    validate_parser.add_argument(
        "--skills-dir",
        default="skills",
        help="Skills directory (default: skills)"
    )
    validate_parser.add_argument(
        "--registry",
        default="registry.json",
        help="Registry file (default: registry.json)"
    )
    validate_parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON"
    )

    # Quality command
    quality_parser = subparsers.add_parser("quality", help="Run quality pipeline")
    quality_parser.add_argument(
        "--skills-dir",
        default="skills",
        help="Skills directory (default: skills)"
    )
    quality_parser.add_argument(
        "--registry",
        default="registry.json",
        help="Registry file (default: registry.json)"
    )
    quality_parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmarks (may take a while)"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run skill tests")
    test_parser.add_argument(
        "skill_id",
        nargs="?",
        help="Specific skill ID to test (domain/skill-name), or omit for all"
    )
    test_parser.add_argument(
        "--skills-dir",
        default="skills",
        help="Skills directory (default: skills)"
    )
    test_parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate test files before running"
    )

    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Get skill recommendations")
    recommend_parser.add_argument(
        "query",
        help="Task description or requirement"
    )
    recommend_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=5,
        help="Maximum recommendations (default: 5)"
    )

    # Compose command
    compose_parser = subparsers.add_parser("compose", help="Compose skills together")
    compose_parser.add_argument(
        "--source",
        required=True,
        help="Source skill ID"
    )
    compose_parser.add_argument(
        "--target",
        help="Target skill ID (for sequential composition)"
    )
    compose_parser.add_argument(
        "--goal",
        help="Goal description for auto-composition"
    )
    compose_parser.add_argument(
        "--output",
        "-o",
        help="Output file for composition plan (JSON)"
    )

    # Create-skill command
    create_parser = subparsers.add_parser("create-skill", help="Create a new skill from template")
    create_parser.add_argument("name", help="Name of the skill")
    create_parser.add_argument("--domain", "-d", default="General", help="Skill domain")
    create_parser.add_argument("--template", "-t", default="basic_python", choices=["basic_python", "python_prolog", "sqlite_analysis", "z3_optimization", "quickjs_transform", "llm_decision_maker", "rag_pipeline", "llm_advanced_features"], help="Template to use")
    create_parser.add_argument("--output-dir", default="skills", help="Skills directory")

    # Trace-view command
    trace_parser = subparsers.add_parser("trace-view", help="View skill execution traces")
    trace_parser.add_argument(
        "--file",
        "-f",
        default="logs/skill_telemetry.jsonl",
        help="Telemetry file path"
    )
    trace_parser.add_argument(
        "--skill",
        "-s",
        help="Filter by skill ID"
    )
    trace_parser.add_argument(
        "--last",
        "-l",
        type=int,
        default=5,
        help="Show last N traces"
    )
    trace_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    trace_parser.add_argument(
        "--surface",
        help="Filter by surface name"
    )
    trace_parser.add_argument(
        "--success-only",
        action="store_true",
        help="Show only successful traces"
    )
    trace_parser.add_argument(
        "--failures-only",
        action="store_true",
        help="Show only failed traces"
    )
    trace_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show full span details"
    )

    # Surfaces command
    subparsers.add_parser("surfaces", help="List all registered surfaces")

    # Skill-info command
    skill_info_parser = subparsers.add_parser("skill-info", help="Display full metadata for a skill")
    skill_info_parser.add_argument("skill_id", help="Skill ID (domain/skill-name)")
    skill_info_parser.add_argument(
        "--registry", "-r", default="registry.json", help="Registry file path (default: registry.json)"
    )

    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Execute a DAG-based skill workflow")
    workflow_parser.add_argument("workflow_file", help="Path to workflow definition file (JSON/YAML)")
    workflow_parser.add_argument("--data", "-d", help="Initial input data (JSON string)")
    workflow_parser.add_argument("--registry", "-r", default="registry.json", help="Registry file path")

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
        elif args.command == "validate":
            asyncio.run(_handle_validate(args))
        elif args.command == "quality":
            asyncio.run(_handle_quality(args))
        elif args.command == "test":
            asyncio.run(_handle_test(args))
        elif args.command == "recommend":
            asyncio.run(_handle_recommend(args))
        elif args.command == "compose":
            asyncio.run(_handle_compose(args))
        elif args.command == "create-skill":
            _handle_create_skill(args)
        elif args.command == "trace-view":
            _handle_trace_view(args)
        elif args.command == "surfaces":
            _handle_surfaces(args)
        elif args.command == "skill-info":
            _handle_skill_info(args)
        elif args.command == "workflow":
            asyncio.run(_handle_workflow(args))
    except Exception as e:
        logger.exception("CLI command failed", command=args.command, error=str(e))
        print(f"Error: {e}", file=sys.stderr)
        from em_cubed.skills.telemetry import get_telemetry_collector
        get_telemetry_collector().flush()
        sys.exit(1)
    finally:
        from em_cubed.skills.telemetry import get_telemetry_collector
        get_telemetry_collector().flush()


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

    async def run_async():
        if args.trace:
            # Setup tracing for CLI run
            from em_cubed.skills.telemetry import initialize_telemetry, TelemetryConfig, ExecutionRecord, TraceContext
            from datetime import timezone
            
            initialize_telemetry(TelemetryConfig(log_every_execution=False))
            
            # Actually we need to mock the skill file load too...
            # Simplified: just run directly if it's a surface run
            # But tracing is tied to SkillExecutor.
            # I'll just run it via surface and manually trace it for CLI run if --trace is on
            from datetime import datetime
            record = ExecutionRecord(skill_id="cli_run", timestamp=datetime.now(timezone.utc), success=True, execution_time_ms=0)
            trace_ctx = TraceContext(record)
            
            from em_cubed.skills.executor import TelemetryProxy
            proxies = {name: TelemetryProxy(plugin_manager.get(name), trace_ctx) 
                       for name in plugin_manager.get_available_surfaces()}
            context = {"surfaces": proxies, "skill_input": {}, "trace": trace_ctx}
            context["context"] = context # compatibility
            
            start = asyncio.get_event_loop().time()
            result = await surface.execute(code, context)
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            
            print(json.dumps(result, indent=2))
            
            print(f"\nExecution Trace: {record.trace_id}")
            print(f"Total Time: {elapsed:.1f}ms")
            
            # Record to collector for persistence
            from em_cubed.skills.telemetry import get_telemetry_collector
            get_telemetry_collector().record_execution(record)
            if record.spans:
                print("Sub-surface calls:")
                for span in record.spans:
                    status = "[OK]" if span.success else "[FAIL]"
                    size_info = f" ({len(str(span.input_data)) if span.input_data else 0}b -> {len(str(span.output_data)) if span.output_data else 0}b)"
                    print(f"  {status} {span.surface:<10} | {span.to_dict()['duration_ms']:>6.1f}ms{size_info}")
        else:
            result = await surface.execute(code)
            print(json.dumps(result, indent=2))

    asyncio.run(run_async())


# New command handlers

async def _handle_validate(args):
    """Handle validate command."""
    from em_cubed.skills.quality_pipeline import SkillQualityPipeline

    skills_dir = Path(args.skills_dir)
    registry_file = Path(args.registry)

    if not skills_dir.exists():
        raise ValueError(f"Skills directory does not exist: {skills_dir}")

    plugin_manager = PluginManager()
    pipeline = SkillQualityPipeline(skills_dir, registry_file, plugin_manager)

    print(f"Validating skills in {skills_dir}...")
    results = await pipeline.validate_all_skills()

    if args.json_output:
        output = {k: v.to_dict() for k, v in results.items()}
        print(json.dumps(output, indent=2))
    else:
        valid_count = sum(1 for r in results.values() if r.valid)
        print(f"\nValidation results: {valid_count}/{len(results)} passed\n")
        for skill_id, result in results.items():
            status = "PASS" if result.valid else "FAIL"
            print(f"  [{status}] {skill_id} (score: {result.quality_score:.2f})")
            for issue in result.issues:
                print(f"    - {issue.severity.value}: {issue.message}")


async def _handle_quality(args):
    """Handle quality command."""
    from em_cubed.skills.quality_pipeline import SkillQualityPipeline

    skills_dir = Path(args.skills_dir)
    registry_file = Path(args.registry)

    plugin_manager = PluginManager()
    pipeline = SkillQualityPipeline(skills_dir, registry_file, plugin_manager)

    print("Running quality pipeline...")

    # Validation
    validation_results = await pipeline.validate_all_skills()
    valid_count = sum(1 for r in validation_results.values() if r.valid)
    print(f"  Validation: {valid_count}/{len(validation_results)} passed")

    # Testing
    test_results = await pipeline.test_all_skills()
    print(f"  Testing: {test_results.get('passed', 0)}/{test_results.get('total_tests', 0)} tests passed")

    # Benchmark if requested
    if args.benchmark:
        print("  Running benchmarks...")
        benchmark_results = await pipeline.benchmark_all_skills()
        print(f"  Benchmarked {len(benchmark_results)} skills")

    # Report
    report = pipeline.get_quality_report()
    print("\nQuality Report:")
    print(f"  Total skills: {report['total_skills']}")
    print(f"  Passing quality: {report['passing_quality']}")
    print(f"  Pass rate: {report['pass_rate']:.1%}")
    print(f"  Registry stats: {report['registry_stats']}")


async def _handle_test(args):
    """Handle test command."""
    from em_cubed.skills.testing import SkillTestRunner
    from em_cubed.plugin_manager import PluginManager
    from em_cubed.skills.quality_pipeline import generate_all_skill_tests

    skills_dir = Path(args.skills_dir)
    registry_file = Path("registry.json")

    # Generate tests if requested
    if args.generate:
        print("Generating test files...")
        generate_all_skill_tests(skills_dir, Path("tests/skills"))

    plugin_manager = PluginManager()
    test_runner = SkillTestRunner(plugin_manager, None)

    if args.skill_id:
        # Test specific skill
        skill_files = list(skills_dir.glob(f"**/{args.skill_id}/SKILL.md"))
        if not skill_files:
            # Try as direct path
            skill_files = [Path(args.skill_id)] if Path(args.skill_id).exists() else []
        if not skill_files:
            print(f"Skill '{args.skill_id}' not found")
            return
        skill_file = skill_files[0]
        metadata = get_skill_metadata(skill_file, skills_dir)
        if metadata:
            # Generate and run tests
            from em_cubed.skills.testing import SkillTestGenerator
            generator = SkillTestGenerator(plugin_manager)
            tests = generator.generate_tests_for_skill(skill_file, metadata)
            summary = await test_runner.run_test_suite(tests, metadata["skill_id"])
            print(f"\nTest Results for {metadata['name']}:")
            print(f"  Passed: {summary['passed']}/{summary['total_tests']}")
            print(f"  Pass rate: {summary['pass_rate']:.1%}")
            print(f"  Duration: {summary['total_duration_ms']:.1f}ms")
        else:
            print(f"Failed to load skill metadata from {skill_file}")
    else:
        # Test all skills
        print("Testing all skills...")
        from em_cubed.skills.quality_pipeline import SkillQualityPipeline
        pipeline = SkillQualityPipeline(skills_dir, registry_file, plugin_manager)
        results = await pipeline.test_all_skills()

        passed = sum(1 for r in results.values() if r.get("passed", 0) > r.get("total_tests", 1) / 2)
        total = len(results)
        print(f"\nOverall: {passed}/{total} skills passed majority of tests\n")
        for skill_id, result in results.items():
            if "error" in result:
                print(f"  [ERROR] {skill_id}: {result['error']}")
            else:
                rate = result.get('pass_rate', 0)
                status = "PASS" if rate >= 0.7 else "FAIL"
                print(f"  [{status}] {skill_id}: pass rate {rate:.1%}")


async def _handle_recommend(args):
    """Handle recommend command."""
    from em_cubed.skills.recommender import SkillRecommender
    from em_cubed.skills.registry import SkillRegistry

    skills_dir = Path("skills")
    registry_file = Path("registry.json")

    registry = SkillRegistry(skills_dir, registry_file)
    recommender = SkillRecommender(registry)

    results = recommender.get_recommendations_for_task(args.query, limit=args.limit)

    print(f"\nRecommendations for: '{args.query}'\n")
    for i, rec in enumerate(results, 1):
        print(f"{i}. {rec.name} ({rec.skill_id})")
        print(f"   Relevance: {rec.relevance_score:.2%}")
        if rec.matching_criteria:
            print(f"   Matches: {', '.join(rec.matching_criteria[:3])}")
        if rec.composition_opportunities:
            print(f"   Can compose with: {', '.join(rec.composition_opportunities[:2])}")
        print()


async def _handle_compose(args):
    """Handle compose command."""
    from em_cubed.skills.composer import SkillComposer, CompositionPlan, CompositionStep, CompositionPattern
    from em_cubed.skills.registry import SkillRegistry
    from em_cubed.plugin_manager import PluginManager
    import json

    skills_dir = Path("skills")
    registry_file = Path("registry.json")

    plugin_manager = PluginManager()
    registry = SkillRegistry(skills_dir, registry_file)
    composer = SkillComposer(plugin_manager, registry)

    if args.source and args.target:
        # Simple two-skill composition
        step = CompositionStep(
            skill_id=args.source,
            input_mapping={"input": "input"},
            output_mapping={"result": "output"},
        )
        plan = CompositionPlan(
            name=f"{args.source}->{args.target}",
            steps=[step],
            pattern=CompositionPattern.SEQUENTIAL,
        )

        result = await composer.compose(plan, {"input": {}})
        print(f"\nComposition result: {'SUCCESS' if result.success else 'FAILED'}")
        if result.success:
            print(f"Output: {result.get_output()}")
        else:
            print(f"Error: {result.error}")
    elif args.goal:
        # Auto-compose based on goal
        plans = composer.suggest_composition(args.source, args.goal)
        print(f"\nSuggested compositions for '{args.goal}':\n")
        for i, plan in enumerate(plans, 1):
            print(f"{i}. {plan.name}")
            for step in plan.steps:
                print(f"   - {step.skill_id}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump([p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in plans], f, indent=2)
            print(f"\nCompositions saved to {args.output}")


def _handle_create_skill(args):
    """Handle create-skill command."""
    name = args.name
    domain = args.domain
    template_name = args.template
    output_base = Path(args.output_dir)

    # Sanitize skill ID
    safe_name = name.lower().replace(" ", "-")
    skill_dir = output_base / domain / safe_name
    skill_file = skill_dir / "SKILL.md"

    if skill_file.exists():
        print(f"Error: Skill already exists at {skill_file}")
        return

    # Load template
    template_path = Path(__file__).parent / "templates" / f"{template_name}.md.j2"
    if not template_path.exists():
        print(f"Error: Template {template_name} not found at {template_path}")
        return

    template_content = template_path.read_text(encoding="utf-8")

    # Render using Jinja2
    from jinja2 import Template
    template = Template(template_content)
    content = template.render(
        name=name,
        domain=domain,
        purpose=f"A {name} skill.",
        description=f"Detailed description for {name}."
    )

    # Write file
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(content, encoding="utf-8")

    print(f"Created new skill: {name}")
    print(f"Location: {skill_file}")
    print(f"Skill ID: {domain}/{safe_name}")


def _handle_trace_view(args):
    """Handle trace-view command."""
    trace_file = Path(args.file)
    if not trace_file.exists():
        print(f"Trace file not found: {trace_file}")
        return

    traces = []
    with open(trace_file, "r") as f:
        for line in f:
            try:
                trace = json.loads(line)
                # Apply filters
                if args.skill and trace.get("skill_id") != args.skill:
                    continue
                if args.surface:
                    spans = trace.get("spans", [])
                    if not any(s.get("surface") == args.surface for s in spans):
                        continue
                if args.success_only and not trace.get("success"):
                    continue
                if args.failures_only and trace.get("success"):
                    continue
                traces.append(trace)
            except json.JSONDecodeError:
                continue

    if not traces:
        print("No traces found matching the specified filters.")
        return

    # Show last N
    traces_to_show = traces[-args.last:]

    if args.json:
        print(json.dumps(traces_to_show, indent=2))
        return

    for trace in traces_to_show:
        status_icon = "âœ“" if trace.get("success") else "âœ—"
        print(f"\n{status_icon} Trace: {trace.get('trace_id')} | Skill: {trace.get('skill_id')}")
        print(f"  Status: {'[OK]' if trace.get('success') else '[FAIL]'} | Time: {trace.get('execution_time_ms', 0):.1f}ms")
        print(f"  Surface: {trace.get('surface', 'unknown')} | Timestamp: {trace.get('timestamp', 'N/A')}")
        spans = trace.get("spans", [])
        if spans:
            print("  Sub-surface calls:")
            for i, span in enumerate(spans):
                span_status = "âœ“" if span.get("success") else "âœ—"
                indent = "    " * (i + 1)
                size_info = f" ({span.get('input_size', 0)}b -> {span.get('output_size', 0)}b)"
                print(f"  {indent}{span_status} [{span.get('surface'):<10}] {span.get('duration_ms', 0):>6.1f}ms{size_info}")
                if args.verbose and span.get("error"):
                    print(f"  {indent}  Error: {span['error']}")
                if args.verbose and span.get("input_data"):
                    inp = str(span["input_data"])
                    if len(inp) > 100:
                        inp = inp[:100] + "..."
                    print(f"  {indent}  Input: {inp}")
                if args.verbose and span.get("output_data"):
                    out = str(span["output_data"])
                    if len(out) > 100:
                        out = out[:100] + "..."
                    print(f"  {indent}  Output: {out}")
        elif args.verbose:
            print("  No sub-surface spans recorded.")


def _handle_surfaces(args):
    """Handle surfaces command to list all registered surfaces."""
    pm = PluginManager()
    info = pm.get_surface_info()

    # Determine load status: eager (instantiated) vs lazy (not yet loaded)
    load_status = {}
    for name in pm._plugins:
        load_status[name] = "eager"
    for name in pm._lazy_classes:
        load_status[name] = "lazy"

    # Print table header
    header = f"{'SURFACE':<12} {'AVAILABLE':<10} {'LOADED':<10} {'DESCRIPTION'}"
    separator = "-" * 12 + " " + "-" * 10 + " " + "-" * 10 + " " + "-" * 40
    print(header)
    print(separator)
    for item in info:
        name = item["name"]
        avail = "yes" if item["available"] else "no"
        loaded = load_status.get(name, "?")
        desc = item.get("description", "")
        print(f"{name:<12} {avail:<10} {loaded:<10} {desc}")


def _handle_skill_info(args):
    """Handle skill-info command to display skill metadata."""
    skill_id = args.skill_id
    registry_path = Path(args.registry)

    # Default skills_dir relative to registry or cwd?
    # Assume skills directory is in default location 'skills'
    skills_dir = Path("skills")

    from em_cubed.skills.registry import SkillRegistry
    if not registry_path.exists():
        print(f"Error: Registry file not found at {registry_path}")
        sys.exit(1)

    registry = SkillRegistry(skills_dir, registry_path)
    metadata = registry.get_skill(skill_id)
    if not metadata:
        print(f"Skill '{skill_id}' not found in registry")
        sys.exit(1)

    # Print metadata
    print(f"Skill ID        : {metadata.skill_id}")
    print(f"Name            : {metadata.name}")
    print(f"Domain          : {metadata.domain}")
    print(f"Version         : {metadata.version}")
    print(f"Surfaces        : {', '.join(metadata.surfaces)}")
    print(f"Purpose         : {metadata.purpose}")
    print(f"Description     : {metadata.description}")
    print(f"Path            : {metadata.path}")
    qm = registry.get_quality(skill_id)
    if qm:
        print(f"Validation Score: {qm.validation_score:.2f}")
        print(f"Test Coverage   : {qm.test_coverage:.2f}")
        print(f"Success Rate    : {qm.success_rate:.2f}")
        print(f"Avg Exec Time   : {qm.avg_execution_time:.2f}ms")
        print(f"Usage Count     : {qm.usage_count}")
    else:
        print("Quality metrics : not available")



async def _handle_workflow(args):
    """Handle workflow command to execute a DAG of skills."""
    workflow_path = Path(args.workflow_file)
    registry_path = Path(args.registry)
    if not workflow_path.exists():
        print(f"Error: Workflow file not found at {workflow_path}")
        sys.exit(1)
    try:
        with open(workflow_path, encoding="utf-8") as f:
            if workflow_path.suffix == ".json":
                wf_data = json.load(f)
            elif workflow_path.suffix in (".yaml", ".yml"):
                import yaml
                wf_data = yaml.safe_load(f)
            else:
                print(f"Error: Unsupported workflow file format: {workflow_path.suffix}")
                sys.exit(1)
    except Exception as e:
        print(f"Error loading workflow: {e}")
        sys.exit(1)
    initial_data = {}
    if args.data:
        try:
            initial_data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error parsing initial data JSON: {e}")
            sys.exit(1)
    from em_cubed.skills.workflow import WorkflowExecutor, WorkflowDefinition, WorkflowStep
    from em_cubed.skills.registry import SkillRegistry
    from em_cubed.skills.composer import SkillComposer
    from em_cubed.plugin_manager import PluginManager
    pm = PluginManager()
    registry = SkillRegistry(Path("skills"), registry_path)
    composer = SkillComposer(pm, registry)
    executor = WorkflowExecutor(composer)
    steps = []
    for s_data in wf_data.get("steps", []):
        steps.append(WorkflowStep(
            id=s_data["id"],
            skill_id=s_data["skill_id"],
            input_mapping=s_data.get("input_mapping", {}),
            output_mapping=s_data.get("output_mapping", {}),
            dependencies=s_data.get("dependencies", []),
            condition=s_data.get("condition"),
            timeout=s_data.get("timeout")
        ))
    workflow = WorkflowDefinition(
        name=wf_data.get("name", workflow_path.stem),
        steps=steps,
        description=wf_data.get("description"),
        timeout=wf_data.get("timeout")
    )
    print(f"Executing workflow: {workflow.name} ({len(workflow.steps)} steps)...")
    result = await executor.execute(workflow, initial_data)
    if result.success:
        print("\nWorkflow completed successfully!")
        print(f"Steps executed: {result.steps_executed}")
        print("\nFinal Output:")
        print(json.dumps(result.get_output(), indent=2))
    else:
        print(f"\nWorkflow failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

