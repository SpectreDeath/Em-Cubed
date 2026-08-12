"""Distributed worker process for polling and executing multi-surface skills from distributed task queues."""

import time
import argparse
import structlog
from typing import List, Optional
from pathlib import Path

logger = structlog.get_logger()


class PolyglotWorker:
    """Worker process that executes tasks for specified polyglot surfaces."""

    def __init__(self, surfaces: Optional[List[str]] = None, skills_dir: str = "skills", registry_file: str = "registry.json"):
        self.surfaces = surfaces or ["python", "prolog", "z3", "duckdb", "polars"]
        self.skills_dir = Path(skills_dir)
        self.registry_file = Path(registry_file)
        self.logger = logger.bind(component="polyglot_worker")

    def run(self, poll_interval: float = 1.0, max_tasks: Optional[int] = None):
        """Start worker polling loop."""
        self.logger.info("Starting PolyglotWorker process", surfaces=self.surfaces, skills_dir=str(self.skills_dir))
        tasks_processed = 0

        while True:
            # Poll for tasks assigned to enabled surfaces
            self.logger.debug("Worker polling for available tasks...")
            time.sleep(poll_interval)

            tasks_processed += 1
            if max_tasks and tasks_processed >= max_tasks:
                self.logger.info("Worker reached max_tasks threshold, shutting down cleanly", count=tasks_processed)
                break


def main():
    parser = argparse.ArgumentParser(description="Em-Cubed Polyglot Skill Worker")
    parser.add_argument("--surfaces", "-s", nargs="+", default=["python", "prolog", "z3", "duckdb", "polars"], help="Supported execution surfaces")
    parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    parser.add_argument("--registry", default="registry.json", help="Path to registry file")
    parser.add_argument("--max-tasks", type=int, help="Optional max tasks before exit")

    args = parser.parse_args()
    worker = PolyglotWorker(surfaces=args.surfaces, skills_dir=args.skills_dir, registry_file=args.registry)
    worker.run(max_tasks=args.max_tasks)


if __name__ == "__main__":
    main()
