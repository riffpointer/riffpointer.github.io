from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen


DEFAULT_GITHUB_OWNER = "riffpointer"
GITHUB_WEB_MODE = "web"
GITHUB_API_MODE = "api"
APP_USER_AGENT = "RiffPointer Project Manager/1.0.0"


def github_repositories_url(owner: str) -> str:
    return f"https://github.com/{quote(owner.strip('/'))}?tab=repositories"


def github_repositories_api_url(owner: str) -> str:
    return f"https://api.github.com/users/{quote(owner.strip('/'))}/repos"


def fetch_github_repositories(
    owner: str = DEFAULT_GITHUB_OWNER,
    extraction_mode: str = GITHUB_WEB_MODE,
    progress: Callable[[int, str], bool] | None = None,
) -> list[dict[str, Any]]:
    if extraction_mode == GITHUB_API_MODE:
        return fetch_github_repositories_from_api(owner, progress)
    return fetch_github_repositories_from_web(owner, progress)


def fetch_github_repositories_from_web(
    owner: str,
    progress: Callable[[int, str], bool] | None = None,
) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    seen_pages: set[str] = set()
    next_url = github_repositories_url(owner)
    for page_index in range(10):
        if next_url in seen_pages:
            break
        seen_pages.add(next_url)
        if progress and progress(min(85, 5 + page_index * 8), f"Fetching repositories page {page_index + 1}..."):
            raise RuntimeError("Autocrawler canceled")
        html = _fetch_text(next_url)
        if progress and progress(min(88, 8 + page_index * 8), f"Parsing repositories page {page_index + 1}..."):
            raise RuntimeError("Autocrawler canceled")
        parser = GitHubRepositoriesParser(owner)
        parser.feed(html)
        parser.close()
        repositories.extend(parser.repositories)
        if progress and progress(min(90, 12 + page_index * 8), f"Found {len(repositories)} repositories so far..."):
            raise RuntimeError("Autocrawler canceled")
        if not parser.next_url:
            break
        next_url = urljoin(next_url, parser.next_url)
    return repositories


def fetch_github_repositories_from_api(
    owner: str,
    progress: Callable[[int, str], bool] | None = None,
) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    seen_pages: set[str] = set()
    next_url = f"{github_repositories_api_url(owner)}?per_page=100&type=owner"
    for page_index in range(10):
        if next_url in seen_pages:
            break
        seen_pages.add(next_url)
        if progress and progress(min(85, 5 + page_index * 8), f"Fetching repositories API page {page_index + 1}..."):
            raise RuntimeError("Autocrawler canceled")
        page, next_page_url = _fetch_json_page(next_url)
        if not isinstance(page, list):
            raise ValueError("GitHub API returned an unexpected response shape.")
        repositories.extend(_repository_from_api(repo) for repo in page if isinstance(repo, dict))
        if progress and progress(min(90, 12 + page_index * 8), f"Loaded {len(repositories)} repositories from API so far..."):
            raise RuntimeError("Autocrawler canceled")
        if not next_page_url:
            break
        next_url = next_page_url
    return repositories


def _repository_from_api(repo: dict[str, Any]) -> dict[str, Any]:
    extracted = dict(repo)
    repo_name = str(repo.get("name") or "").strip()
    if repo_name:
        extracted["id"] = repo_name
        extracted["name"] = repo_name
    return extracted


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": APP_USER_AGENT,
        },
    )
    with urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _fetch_json_page(url: str) -> tuple[Any, str]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": APP_USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read().decode(charset, errors="replace")
        return json.loads(body), _next_link_from_header(response.headers.get("Link", ""))


def _next_link_from_header(header: str) -> str:
    for part in header.split(","):
        section = part.strip()
        match = re.match(r'<([^>]+)>;\s*rel="next"', section)
        if match:
            return match.group(1)
    return ""


class GitHubRepositoriesParser(HTMLParser):
    def __init__(self, owner: str) -> None:
        super().__init__(convert_charrefs=True)
        self.owner = owner.strip("/")
        self.repositories: list[dict[str, Any]] = []
        self.next_url = ""
        self._current: dict[str, Any] | None = None
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "a" and attributes.get("rel") == "next" and attributes.get("href"):
            self.next_url = attributes["href"]
        itemprop = attributes.get("itemprop", "")
        if tag == "a" and "codeRepository" in itemprop:
            repo_id = self._repo_id_from_href(attributes.get("href", ""))
            if not repo_id:
                return
            self._current = {"id": repo_id, "name": "", "description": "", "language": "", "fork": False}
            self.repositories.append(self._current)
            self._capture = "name"
            return
        if self._current is None:
            return
        if tag == "p" and itemprop == "description":
            self._capture = "description"
            return
        if tag == "span" and itemprop == "programmingLanguage":
            self._capture = "language"

    def handle_endtag(self, tag: str) -> None:
        if self._capture == "name" and tag == "a":
            self._capture = None
        elif self._capture == "description" and tag == "p":
            self._capture = None
        elif self._capture == "language" and tag == "span":
            self._capture = None

    def handle_data(self, data: str) -> None:
        if self._current is None:
            return
        value = unescape(data).strip()
        if not value:
            return
        if "forked from" in value.casefold():
            self._current["fork"] = True
            return
        if self._capture is None:
            return
        existing = str(self._current.get(self._capture, ""))
        self._current[self._capture] = " ".join(part for part in (existing, value) if part).strip()

    def _repo_id_from_href(self, href: str) -> str:
        match = re.fullmatch(rf"/{re.escape(self.owner)}/([^/?#]+)", href.strip())
        return match.group(1) if match else ""
