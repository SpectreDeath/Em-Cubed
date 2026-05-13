#!/usr/bin/env python3
"""
Cangjie Migration Validation Script

Simple static analysis to compare SKILL.md vs SKILL_CANGJIE.md files.
Measures file size, code patterns, and surface orchestration metrics.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent
SKILLS_DIR = PROJECT_ROOT / "skills"
OUTPUT_REPORT = PROJECT_ROOT / "cangjie_comparison_report.md"


@dataclass
class Metrics:
    file_size: int
    code_lines: int
    surface_calls: int
    function_count: int
    struct_count: int


def collect_metrics(file_path: Path) -> Metrics:
    """Extract basic metrics from a skill Markdown file."""
    if not file_path.exists():
        return Metrics(0, 0, 0, 0, 0)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Code lines: lines that look like actual code (not just Markdown)
    # Heuristics: starts with keyword, brace, or indented code pattern
    code_line_patterns = [
        r'^\s*(func|struct|enum|typealias|let|var)\s+',
        r'^\s*[a-z_][a-z0-9_]*\s*\(.*\)\s*\{',
        r'^\s*[A-Z_][A-Z0-9_]*\s*\{',
        r'^\s*}',
        r'^\s*//.*(perform|call_surface|surface)',
        r'^\s*//.*(for|if|while|switch|return)',
        r'^\s*import\s+\w+',
        r'^\s*from\s+\w+',
        r'^\s*def\s+\w+',
        r'^\s*class\s+\w+',
    ]

    code_lines = 0
    for line in lines:
        stripped = line.strip()
        if stripped and any(re.match(p, line) for p in code_line_patterns):
            code_lines += 1

    # Surface calls: cross-surface orchestration patterns
    surface_patterns = [
        r'perform\s+EmCubed\.call_surface',
        r'EmCubed\.from_surface',
        r'call_surface',
        r'from_surface',
    ]
    surface_calls = sum(len(re.findall(p, content)) for p in surface_patterns)

    # Function definitions
    func_pattern = r'^\s*(?:public\s+)?func\s+\w+\s*\([^)]*\)'
    function_count = sum(1 for line in lines if re.match(func_pattern, line))

    # Struct definitions
    struct_pattern = r'^\s*struct\s+\w+'
    struct_count = sum(1 for line in lines if re.match(struct_pattern, line))

    return Metrics(
        file_size=file_path.stat().st_size,
        code_lines=code_lines,
        surface_calls=surface_calls,
        function_count=function_count,
        struct_count=struct_count,
    )


def find_skill_pairs() -> List[Tuple[Path, Path]]:
    """Find all (SKILL.md, SKILL_CANGJIE.md) pairs."""
    pairs = []

    if not SKILLS_DIR.exists():
        print(f"Error: {SKILLS_DIR} not found")
        return pairs

    for category in sorted(SKILLS_DIR.iterdir()):
        if not category.is_dir():
            continue
        for skill in sorted(category.iterdir()):
            if not skill.is_dir():
                continue
            orig = skill / "SKILL.md"
            cj = skill / "SKILL_CANGJIE.md"
            if orig.exists() and cj.exists():
                pairs.append((orig, cj))

    return pairs


def compare_pair(orig: Path, cj: Path) -> Dict:
    """Compare metrics between original and Cangjie versions."""
    skill_name = orig.parent.name
    skill_category = orig.parent.parent.name
    skill_id = f"{skill_category}/{skill_name}"

    orig_metrics = collect_metrics(orig)
    cj_metrics = collect_metrics(cj)

    # Compute improvements
    loc_diff = cj_metrics.code_lines - orig_metrics.code_lines
    loc_pct = (loc_diff / orig_metrics.code_lines * 100) if orig_metrics.code_lines else 0
    surf_diff = cj_metrics.surface_calls - orig_metrics.surface_calls
    surf_pct = (surf_diff / orig_metrics.surface_calls * 100) if orig_metrics.surface_calls else 0

    # Orchestration complexity heuristic
    orig_complex = orig_metrics.surface_calls * 10 + orig_metrics.function_count * 5
    cj_complex = cj_metrics.surface_calls * 10 + cj_metrics.function_count * 5
    complex_diff_pct = ((orig_complex - cj_complex) / orig_complex * 100) if orig_complex else 0

    return {
        "skill": skill_id,
        "path": str(orig.parent.relative_to(PROJECT_ROOT)),
        "orig": orig_metrics,
        "cj": cj_metrics,
        "loc_diff": loc_diff,
        "loc_pct": loc_pct,
        "surf_diff": surf_diff,
        "surf_pct": surf_pct,
        "complex_diff_pct": complex_diff_pct,
    }


def main():
    print("=" * 60)
    print("Em-Cubed Cangjie Migration Validation")
    print("=" * 60)

    pairs = find_skill_pairs()
    print(f"\nFound {len(pairs)} skill pairs to analyze.\n")

    if not pairs:
        print("No SKILL.md / SKILL_CANGJIE.md pairs found.")
        return 0

    results = []
    for orig, cj in pairs:
        comp = compare_pair(orig, cj)
        results.append(comp)

        skill = comp["skill"]
        orig_m = comp["orig"]
        cj_m = comp["cj"]

        print(f"\n{skill}")
        print(f"  File sizes:   orig={orig_m.file_size:6,}  cj={cj_m.file_size:6,}  (change {cj_m.file_size - orig_m.file_size:+,})")
        print(f"  Code lines:   orig={orig_m.code_lines:4d}  cj={cj_m.code_lines:4d}  ({comp['loc_pct']:+.1f}%)")
        print(f"  Surface calls: orig={orig_m.surface_calls:3d}  ->  cj={cj_m.surface_calls:3d}  ({comp['surf_pct']:+.1f}%)")
        print(f"  Functions:    orig={orig_m.function_count:3d}  cj={cj_m.function_count:3d}")
        print(f"  Structs:      orig={orig_m.struct_count:3d}  cj={cj_m.struct_count:3d}")
        print(f"  Orchestration complexity change: {comp['complex_diff_pct']:+.1f}%")

    # Totals
    total_orig_loc = sum(r["orig"].code_lines for r in results)
    total_cj_loc = sum(r["cj"].code_lines for r in results)
    total_surface_calls_orig = sum(r["orig"].surface_calls for r in results)
    total_surface_calls_cj = sum(r["cj"].surface_calls for r in results)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"  Total LOC:          {total_orig_loc:,} -> {total_cj_loc:,}  (change {total_cj_loc - total_orig_loc:+,}, {((total_cj_loc - total_orig_loc)/total_orig_loc*100):+.1f}%)")
    print(f"  Total surface calls: {total_surface_calls_orig:,} -> {total_surface_calls_cj:,}  (change {total_surface_calls_cj - total_surface_calls_orig:+,})")
    print(f"  Skills analyzed:    {len(results)}")

    # Generate report markdown
    report_lines = [
        "# Cangjie Migration Validation Report",
        "",
        f"**Generated:** {len(results)} skill pairs analyzed",
        "",
        "## Overall Metrics",
        "",
        f"| Metric | Original | Cangjie | Change |",
        f"|--------|---------|--------|--------|",
        f"| Total LOC | {total_orig_loc:,} | {total_cj_loc:,} | {total_cj_loc - total_orig_loc:+,} ({((total_cj_loc - total_orig_loc)/total_orig_loc*100):.1f}%) |",
        f"| Surface calls | {total_surface_calls_orig:,} | {total_surface_calls_cj:,} | {total_surface_calls_cj - total_surface_calls_orig:+,} |",
        "",
        "## Per-Skill Comparison",
        "",
        f"| Skill | LOC (orig->CJ) | Surface calls (orig->CJ) | Complexity improvement |",
        f"|-------|---------------|--------------------------|------------------------|",
    ]

    for r in results:
        report_lines.append(
            f"| {r['skill']} | {r['orig'].code_lines:,} -> {r['cj'].code_lines:,} | "
            f"{r['orig'].surface_calls} -> {r['cj'].surface_calls} | {r['complex_diff_pct']:+.1f}% |"
        )

    report_lines.extend([
        "",
        "## Interpretation",
        "",
        "- **LOC reduction**: Cangjie consolidates orchestration logic, reducing overall lines of coordination code.",
        "- **Surface calls**: Fewer cross-surface transitions indicate tighter integration.",
        "- **Orchestration complexity**: Lower score suggests simpler coordination patterns.",
        "",
        "These metrics are approximations from static analysis and serve as a high-level validation.",
        "",
        "## Next Steps",
        "",
        "1. Deep-dive analysis of top-performing skills for pattern extraction.",
        "2. Create migration guidelines based on successful transformations.",
        "3. Extend migration to additional multi-surface skills.",
        "",
    ])

    report_md = '\n'.join(report_lines)
    OUTPUT_REPORT.write_text(report_md, encoding='utf-8')
    print(f"\nReport saved: {OUTPUT_REPORT.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[Interrupted]")
        sys.exit(130)
