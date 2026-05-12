from __future__ import annotations

import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Any


ProgressCallback = Callable[[int, str], None]


@dataclass
class LinkCheckIssue:
    label: str
    url: str
    issue_type: str
    detail: str


@dataclass
class LinkCheckResult:
    checked: int
    issues: list[LinkCheckIssue]


def build_project_links(project: dict[str, Any], github_owner: str) -> list[tuple[str, str]]:
    project_id = str(project.get("id", "")).strip()
    links: list[tuple[str, str]] = []
    if project_id:
        links.append(("GitHub", f"https://github.com/{github_owner}/{project_id}"))
        links.append(("Demo", f"https://{github_owner.lower()}.github.io/{project_id}"))
    for key, label in (("demo_url", "Demo"), ("documentation_url", "Documentation"), ("docs_url", "Documentation")):
        value = str(project.get(key, "")).strip()
        if value:
            links.append((label, value))
    return links


def check_project_links(projects: list[dict[str, Any]], github_owner: str, progress: ProgressCallback | None = None) -> LinkCheckResult:
    issues: list[LinkCheckIssue] = []
    checked = 0
    total = max(len(projects), 1)
    opener = urllib.request.build_opener(NoRedirectHandler())

    for index, project in enumerate(projects):
        for label, url in build_project_links(project, github_owner):
            checked += 1
            if progress:
                step = int((checked / max(total * 3, 1)) * 100)
                progress(step, f"Checking {label}: {url}")
            issue = _check_url(opener, url, label)
            if issue is not None:
                issues.append(issue)
        if progress:
            progress(int(((index + 1) / total) * 100), f"Checked {index + 1} of {total} projects")
    if progress:
        progress(100, "Link check complete")
    return LinkCheckResult(checked=checked, issues=issues)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def _check_url(opener, url: str, label: str) -> LinkCheckIssue | None:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "RiffPointer-Project-Manager"})
    try:
        with opener.open(request, timeout=10) as response:
            status = getattr(response, "status", response.getcode())
            if 200 <= status < 400:
                return None
            if status == 404:
                return LinkCheckIssue(label, url, "404", "Not found")
            return LinkCheckIssue(label, url, f"HTTP {status}", "Unexpected HTTP response")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return LinkCheckIssue(label, url, "404", "Not found")
        if 300 <= exc.code < 400:
            return LinkCheckIssue(label, url, "redirect-loop", f"Redirect problem: {exc}")
        return LinkCheckIssue(label, url, f"HTTP {exc.code}", exc.reason or "HTTP error")
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, ssl.SSLError):
            return LinkCheckIssue(label, url, "ssl", str(reason))
        if "ssl" in str(reason).lower():
            return LinkCheckIssue(label, url, "ssl", str(reason))
        if "redirect" in str(reason).lower():
            return LinkCheckIssue(label, url, "redirect-loop", str(reason))
        return LinkCheckIssue(label, url, "network", str(reason))
    except ssl.SSLError as exc:
        return LinkCheckIssue(label, url, "ssl", str(exc))
