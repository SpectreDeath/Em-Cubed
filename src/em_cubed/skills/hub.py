"""Skill Hub package manager for remote skill installation, lockfile generation (em3.lock), and SHA-256 signing."""

import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from typing import Any
import structlog

logger = structlog.get_logger()


class SkillHub:
    """Manage skill package installation, lockfile verification, and integrity signing."""

    def __init__(self, skills_dir: Path | None = None, lockfile_path: Path | None = None):
        self.skills_dir = skills_dir or Path("skills")
        self.lockfile_path = lockfile_path or Path("em3.lock")
        logger.info("SkillHub initialized", skills_dir=str(self.skills_dir), lockfile=str(self.lockfile_path))

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def generate_lockfile(self) -> dict[str, Any]:
        """Scan local skills directory and generate em3.lock lockfile payload."""
        lock_entries: dict[str, Any] = {}

        if self.skills_dir.exists():
            for skill_file in self.skills_dir.glob("**/*.md"):
                if skill_file.name in ("README.md", "CONTRIBUTING.md"):
                    continue
                rel_path = skill_file.relative_to(self.skills_dir).as_posix()
                file_hash = self.compute_sha256(skill_file)
                lock_entries[rel_path] = {
                    "sha256": file_hash,
                    "size_bytes": skill_file.stat().st_size,
                    "path": rel_path,
                }

        payload = {
            "version": "1.0",
            "skill_count": len(lock_entries),
            "skills": lock_entries,
        }

        with open(self.lockfile_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info("Generated lockfile", path=str(self.lockfile_path), count=len(lock_entries))
        return payload

    def verify_skill_integrity(self, rel_path: str) -> dict[str, Any]:
        """Verify local skill file against em3.lock signature."""
        if not self.lockfile_path.exists():
            self.generate_lockfile()

        try:
            with open(self.lockfile_path, encoding="utf-8") as f:
                lock_data = json.load(f)

            entries = lock_data.get("skills", {})
            if rel_path not in entries:
                return {"valid": False, "reason": f"Skill path '{rel_path}' not found in em3.lock"}

            target_file = self.skills_dir / rel_path
            if not target_file.exists():
                return {"valid": False, "reason": f"File '{target_file}' does not exist"}

            current_hash = self.compute_sha256(target_file)
            expected_hash = entries[rel_path].get("sha256")

            if current_hash == expected_hash:
                return {"valid": True, "sha256": current_hash}
            else:
                return {
                    "valid": False,
                    "reason": f"Hash mismatch for '{rel_path}': expected {expected_hash}, got {current_hash}",
                }
        except Exception as e:
            return {"valid": False, "reason": str(e)}

    def install_skill(self, source: str, target_name: str | None = None) -> dict[str, Any]:
        """Install a skill from a local path or HTTP URL into skills directory.

        Args:
            source: File path or HTTP/HTTPS URL pointing to a SKILL.md file
            target_name: Optional target filename under skills/Custom/

        Returns:
            Dict with installation status, path, and SHA-256 hash
        """
        dest_dir = self.skills_dir / "Custom"
        dest_dir.mkdir(parents=True, exist_ok=True)

        if source.startswith("http://") or source.startswith("https://"):
            filename = target_name or source.split("/")[-1] or "downloaded_skill.md"
            if not filename.endswith(".md"):
                filename += ".md"
            target_path = dest_dir / filename

            try:
                urllib.request.urlretrieve(source, target_path)  # nosec B310 - user initiated skill install
            except Exception as e:
                logger.exception("Failed to download remote skill", source=source, error=str(e))
                return {"status": "error", "message": f"Download failed: {e!s}"}

        else:
            src_path = Path(source)
            if not src_path.exists():
                return {"status": "error", "message": f"Source file '{source}' does not exist"}

            filename = target_name or src_path.name
            target_path = dest_dir / filename
            shutil.copy2(src_path, target_path)

        file_hash = self.compute_sha256(target_path)
        self.generate_lockfile()

        logger.info("Skill installed successfully", target=str(target_path), hash=file_hash)
        return {
            "status": "ok",
            "path": str(target_path),
            "sha256": file_hash,
        }
