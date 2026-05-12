from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_PROJECT_FIELDS = ("name", "id", "description", "has_demo", "tags")


@dataclass
class JsonMaintenanceResult:
    sorted_keys: bool
    pretty_printed: bool
    schema_valid: bool
    missing_fields: list[str]
    rule_issues: list[str]
    normalized_data: Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def format_and_validate_projects(data: Any) -> JsonMaintenanceResult:
    missing_fields: list[str] = []
    rule_issues: list[str] = []
    schema_valid = True

    if not isinstance(data, list):
        return JsonMaintenanceResult(
            sorted_keys=False,
            pretty_printed=False,
            schema_valid=False,
            missing_fields=["Root JSON value must be a list of project objects."],
            rule_issues=[],
            normalized_data=data,
        )

    normalized_projects: list[Any] = []
    seen_ids: dict[str, int] = {}
    seen_repo_urls: dict[str, int] = {}
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            schema_valid = False
            missing_fields.append(f"Project {index + 1}: expected an object.")
            normalized_projects.append(item if isinstance(item, dict) else {"value": item})
            continue

        project = dict(item)
        project_id = str(project.get("id", "")).strip().casefold()
        if project_id:
            if project_id in seen_ids:
                schema_valid = False
                rule_issues.append(
                    f"Projects {seen_ids[project_id]} and {index + 1}: duplicate slug/id '{project_id}'"
                )
            else:
                seen_ids[project_id] = index + 1
        for key in ("repo_url", "github_url"):
            url = str(project.get(key, "")).strip()
            if url:
                if not _is_valid_http_url(url):
                    schema_valid = False
                    rule_issues.append(f"Project {index + 1}: invalid {key.replace('_', ' ')}")
                if url in seen_repo_urls:
                    schema_valid = False
                    rule_issues.append(
                        f"Projects {seen_repo_urls[url]} and {index + 1}: duplicate repo URL"
                    )
                else:
                    seen_repo_urls[url] = index + 1
        project_missing = [field for field in REQUIRED_PROJECT_FIELDS if field not in project or project[field] in (None, "")]
        if project_missing:
            schema_valid = False
            missing_fields.append(f"Project {index + 1}: missing {', '.join(project_missing)}")
        if "tags" in project and not isinstance(project["tags"], list):
            schema_valid = False
            missing_fields.append(f"Project {index + 1}: tags must be a list")
        _validate_project_rules(project, index + 1, rule_issues)
        normalized_projects.append(project)

    normalized_projects = [
        dict(sorted(project.items(), key=lambda item: item[0].casefold())) if isinstance(project, dict) else project
        for project in normalized_projects
    ]
    return JsonMaintenanceResult(
        sorted_keys=True,
        pretty_printed=True,
        schema_valid=schema_valid,
        missing_fields=missing_fields,
        rule_issues=rule_issues,
        normalized_data=normalized_projects,
    )


def dump_pretty_sorted_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _validate_project_rules(project: dict[str, Any], project_number: int, issues: list[str]) -> None:
    for key in ("image_url", "screenshot_url", "banner_url"):
        url = str(project.get(key, "")).strip()
        if url and not _is_valid_http_url(url):
            issues.append(f"Project {project_number}: invalid {key.replace('_', ' ')}")

    markdown_fields = ("description", "readme", "notes")
    for key in markdown_fields:
        value = str(project.get(key, "")).strip()
        if value and _has_broken_markdown(value):
            issues.append(f"Project {project_number}: broken markdown in {key}")


def _is_valid_http_url(url: str) -> bool:
    return bool(re.match(r"^https?://[^\s]+$", url))


def _has_broken_markdown(text: str) -> bool:
    if text.count("[") != text.count("]"):
        return True
    if text.count("(") != text.count(")"):
        return True
    if re.search(r"\[[^\]]+\]\([^)]+\)", text) is None and ("[" in text or "]" in text or "(" in text or ")" in text):
        return True
    return False
