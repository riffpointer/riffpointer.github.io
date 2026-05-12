from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any


ProgressCallback = Callable[[int, str], None]
CancelCheck = Callable[[], bool]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".bmp", ".svg"}
COMMON_METADATA_FILES = (
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "npm-shrinkwrap.json",
    "Cargo.toml",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "README.txt",
    "index.html",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "astro.config.mjs",
    "svelte.config.js",
    "tsconfig.json",
)


@dataclass
class ScanResult:
    project: dict[str, Any]
    files_scanned: int
    screenshots: list[str]
    metadata_files: list[str]
    tags: list[str]
    completion: str


def scan_project_folder(
    folder: Path,
    progress: ProgressCallback | None = None,
    cancelled: CancelCheck | None = None,
) -> ScanResult:
    folder = folder.expanduser().resolve()
    if progress:
        progress(0, "Scanning folder")
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    files = [path for path in folder.rglob("*") if path.is_file()]
    files_scanned = len(files)
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    metadata_files = []
    screenshots = []
    tags: set[str] = set()
    project_name = folder.name
    description_parts: list[str] = []

    common_files = {path.name.lower(): path for path in files}
    if progress:
        progress(20, "Reading metadata files")
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    package_json = common_files.get("package.json")
    if package_json:
        metadata_files.append(str(package_json.relative_to(folder)))
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
            project_name = str(package.get("name") or project_name)
            description = str(package.get("description") or "").strip()
            if description:
                description_parts.append(description)
            for key in ("keywords", "tags"):
                values = package.get(key)
                if isinstance(values, list):
                    tags.update(_normalize_tag(str(value)) for value in values if str(value).strip())
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            pass

    for candidate in COMMON_METADATA_FILES:
        path = common_files.get(candidate.lower())
        if path and str(path.relative_to(folder)) not in metadata_files:
            metadata_files.append(str(path.relative_to(folder)))

    if progress:
        progress(40, "Detecting screenshots")
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    for file in files:
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            screenshots.append(str(file.relative_to(folder)))
            tags.add("screenshot")

    if progress:
        progress(60, "Generating tags")
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    tags.update(_infer_tags_from_structure(folder, files))
    tags.update(_infer_tags_from_name(folder.name))

    if progress:
        progress(80, "Estimating completion")
    if cancelled and cancelled():
        raise RuntimeError("scan cancelled")

    completion = _estimate_completion(files, metadata_files, screenshots)
    description_parts.extend(_description_from_signals(metadata_files, screenshots, completion))

    if progress:
        progress(100, "Scan complete")

    slug = _slugify(project_name)
    project = {
        "name": project_name,
        "id": slug,
        "description": " ".join(part for part in description_parts if part).strip(),
        "has_demo": any(name in common_files for name in ("index.html", "dist", "build")),
        "tags": sorted(tags),
        "source_path": str(folder),
        "completion_status": completion,
        "screenshots": screenshots,
        "metadata_files": metadata_files,
        "files_scanned": files_scanned,
    }
    return ScanResult(
        project=project,
        files_scanned=files_scanned,
        screenshots=screenshots,
        metadata_files=metadata_files,
        tags=sorted(tags),
        completion=completion,
    )


def _normalize_tag(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower().replace("'", "")).strip("-") or "project"


def _infer_tags_from_structure(folder: Path, files: list[Path]) -> set[str]:
    tags: set[str] = set()
    names = {path.name.lower() for path in files}
    paths = {str(path.relative_to(folder)).replace("\\", "/").lower() for path in files}
    if "package.json" in names:
        tags.add("javascript")
    if "pyproject.toml" in names or any(name.endswith(".py") for name in names):
        tags.add("python")
    if "cargo.toml" in names or any(name.endswith(".rs") for name in names):
        tags.add("rust")
    if "index.html" in names or any(path.startswith("src/") and path.endswith((".html", ".css", ".js", ".ts")) for path in paths):
        tags.add("web")
    if any(path.startswith("assets/") or path.startswith("public/") for path in paths):
        tags.add("assets")
    return tags


def _infer_tags_from_name(name: str) -> set[str]:
    return {tag for tag in (_normalize_tag(part) for part in re.split(r"[\s_-]+", name)) if tag}


def _estimate_completion(files: list[Path], metadata_files: list[str], screenshots: list[str]) -> str:
    score = 0
    names = {path.name.lower() for path in files}
    if "readme.md" in names or "readme.txt" in names:
        score += 20
    if any(name in names for name in ("package.json", "pyproject.toml", "Cargo.toml")):
        score += 25
    if any(path.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")) for path in screenshots):
        score += 15
    if any(path.lower().startswith(("dist/", "build/", "docs/")) for path in metadata_files):
        score += 20
    score += min(20, len(files) // 20)
    if score >= 70:
        return "near-complete"
    if score >= 40:
        return "in-progress"
    return "early-stage"


def _description_from_signals(metadata_files: list[str], screenshots: list[str], completion: str) -> list[str]:
    parts = []
    if metadata_files:
        parts.append(f"Detected {len(metadata_files)} metadata file(s).")
    if screenshots:
        parts.append(f"Found {len(screenshots)} screenshot(s).")
    parts.append(f"Completion status: {completion.replace('-', ' ')}.")
    return parts
