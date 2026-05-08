"""Generate comprehensive tests for all skills.

Run this module to create test files for every skill in the skills directory.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from em_cubed.skills.quality_pipeline import generate_all_skill_tests

def main():
    skills_dir = Path("skills")
    output_dir = Path("tests/skills")

    print(f"Generating tests for skills in {skills_dir}...")
    generate_all_skill_tests(skills_dir, output_dir)

    # Count generated files
    test_files = list(output_dir.glob("test_*.py"))
    print(f"[OK] Generated {len(test_files)} test files")

    # List them
    for tf in sorted(test_files):
        print(f"  - {tf.name}")

if __name__ == "__main__":
    main()
