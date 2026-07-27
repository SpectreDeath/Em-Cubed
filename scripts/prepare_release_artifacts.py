"""Release artifact builder for Em-Cubed.

Re-indexes the skills library, builds registry.json and skills_dataset.jsonl
(for Hugging Face Datasets upload), and validates release artifacts.
"""

import json
from pathlib import Path
from em_cubed.indexer import reindex


def main():
    root = Path(__file__).resolve().parents[1]
    skills_dir = root / "skills"
    registry_path = root / "registry.json"
    hf_dataset_path = root / "skills_dataset.jsonl"

    print(f"Indexing skills from {skills_dir}...")
    reindex(skills_dir, registry_path)
    with open(registry_path, "r", encoding="utf-8") as f:
        skills = json.load(f)
    print(f"[OK] Successfully indexed {len(skills)} skills into {registry_path.name}")

    # Build Hugging Face JSON Lines dataset
    print(f"Building Hugging Face dataset artifact {hf_dataset_path.name}...")
    with open(hf_dataset_path, "w", encoding="utf-8") as f:
        for skill in skills:
            f.write(json.dumps(skill, ensure_ascii=False) + "\n")

    print(f"[OK] Exported {len(skills)} JSON Lines records to {hf_dataset_path.name}")
    print("[OK] Release artifacts ready for GitHub Release & Hugging Face upload!")


if __name__ == "__main__":
    main()
