"""Create a sanitized ZIP backup for ATLAS/EWU runtime data.

The script is intentionally conservative: it backs up only explicitly selected
directories and skips secrets, logs, caches, and temporary files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


EXCLUDED_NAMES = {
    ".env",
    ".env.local",
    ".git",
    "__pycache__",
    ".pytest_cache",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp"}


def create_backup(source_roots: list[Path], output_path: Path) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "output": str(output_path),
        "sources": [str(path) for path in source_roots],
        "files": [],
        "skipped_missing_sources": [],
    }

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        for source_root in source_roots:
            if not source_root.exists():
                manifest["skipped_missing_sources"].append(str(source_root))
                continue
            for file_path in source_root.rglob("*"):
                if not file_path.is_file() or _is_excluded(file_path):
                    continue
                relative_path = Path(source_root.name) / file_path.relative_to(source_root)
                archive.write(file_path, relative_path.as_posix())
                manifest["files"].append(
                    {
                        "path": relative_path.as_posix(),
                        "size_bytes": file_path.stat().st_size,
                        "sha256": _sha256(file_path),
                    }
                )

        archive.writestr("backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    manifest["archive_size_bytes"] = output_path.stat().st_size
    return manifest


def default_source_roots() -> list[Path]:
    roots = []
    atlas_data_dir = os.getenv("ATLAS_DATA_DIR")
    ewu_data_dir = os.getenv("EWU_DATA_DIR")
    if atlas_data_dir:
        roots.append(Path(atlas_data_dir))
    if ewu_data_dir:
        roots.append(Path(ewu_data_dir))
    if not roots:
        project_root = Path(__file__).resolve().parents[1]
        roots.extend([project_root / "data", project_root / "EWU_Data", project_root / "ewu_bot" / "EWU_Data"])
    return roots


def _is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return True
    return path.suffix.lower() in EXCLUDED_SUFFIXES


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a sanitized ATLAS/EWU data backup ZIP.")
    parser.add_argument("--output", type=Path, required=True, help="Target ZIP path.")
    parser.add_argument("--source", type=Path, action="append", default=[], help="Source directory. Can be repeated.")
    args = parser.parse_args()

    sources = args.source or default_source_roots()
    manifest = create_backup([path.resolve() for path in sources], args.output.resolve())
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
