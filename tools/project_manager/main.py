from __future__ import annotations

import json
import os
import re
import shutil
import signal
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None

from PySide6.QtCore import QMimeData, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QKeySequence, QPalette, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QComboBox,
    QPushButton,
    QProgressDialog,
    QStatusBar,
    QStackedWidget,
    QStyleFactory,
    QTableView,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex

from project_scanner import scan_project_folder
from json_tools import dump_pretty_sorted_json, format_and_validate_projects, load_json
from link_checker import check_project_links
from github_autocrawler import (
    DEFAULT_GITHUB_OWNER,
    GITHUB_API_MODE,
    GITHUB_WEB_MODE,
    fetch_github_repositories,
    github_repositories_api_url,
    github_repositories_url,
)


APP_NAME = "RiffPointer Project Manager"
APP_VERSION = "1.0.0"
ORG_NAME = "RiffPointer"
PROJECT_COLUMNS = ("Name", "ID", "Demo", "Tags", "Description")
THEME_OPTIONS = ("auto", "light", "dark")
REPOSITORY_URL = "https://github.com/riffpointer/riffpointer.github.io/"
GITHUB_REPOSITORIES_URL = f"https://github.com/{DEFAULT_GITHUB_OWNER}?tab=repositories"
COMPACT_ROW_HEIGHT = 22
COMPACT_HEADER_HEIGHT = 22
DEFAULT_ROW_HEIGHT = 28
DEFAULT_HEADER_HEIGHT = 28

TAG_INFERENCE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("python", ("python", "pyproject", "pip", "django", "flask", "fastapi", "streamlit", "pyside", "pyqt", "tkinter", "kivy")),
    ("javascript", ("javascript", "js", "node.js", "nodejs", "npm", "yarn", "pnpm", "react", "vue", "svelte", "angular", "express")),
    ("typescript", ("typescript", "ts", "tsx", "next.js", "nextjs", "nuxt", "nestjs", "vite")),
    ("html", ("html", "html5")),
    ("css", ("css", "css3", "tailwind", "bootstrap", "sass", "scss", "less")),
    ("rust", ("rust", "cargo", "tauri", "actix", "rocket.rs", "axum")),
    ("go", ("go", "golang", "gin", "fiber", "echo framework")),
    ("java", ("java", "spring", "spring boot", "gradle", "maven", "android")),
    ("kotlin", ("kotlin", "ktor", "jetpack compose")),
    ("swift", ("swift", "swiftui", "uikit", "ios", "macos")),
    ("csharp", ("c#", "csharp", ".net", "dotnet", "asp.net", "blazor", "wpf", "winforms", "unity")),
    ("cpp", ("c++", "cpp", "qt", "wxwidgets", "unreal engine")),
    ("c", ("c language", "gtk")),
    ("php", ("php", "laravel", "symfony", "wordpress", "codeigniter", "drupal")),
    ("ruby", ("ruby", "rails", "ruby on rails", "sinatra")),
    ("dart", ("dart", "flutter")),
    ("lua", ("lua", "love2d", "löve")),
    ("react", ("react", "react.js", "reactjs", "tsx", "jsx")),
    ("nextjs", ("next.js", "nextjs")),
    ("vue", ("vue", "vue.js", "vuejs", "nuxt")),
    ("nuxt", ("nuxt", "nuxt.js", "nuxtjs")),
    ("svelte", ("svelte", "sveltekit")),
    ("angular", ("angular", "angularjs")),
    ("solidjs", ("solid", "solidjs", "solid.js")),
    ("astro", ("astro", "astro.js")),
    ("remix", ("remix", "remix.run")),
    ("vite", ("vite", "vitest")),
    ("tailwind", ("tailwind", "tailwindcss")),
    ("bootstrap", ("bootstrap", "bootstrap css")),
    ("django", ("django",)),
    ("flask", ("flask",)),
    ("fastapi", ("fastapi", "fast api")),
    ("streamlit", ("streamlit",)),
    ("express", ("express", "express.js", "expressjs")),
    ("nestjs", ("nestjs", "nest.js")),
    ("electron", ("electron", "electron.js")),
    ("tauri", ("tauri",)),
    ("pyside", ("pyside", "pyside2", "pyside6", "qt for python")),
    ("pyqt", ("pyqt", "pyqt5", "pyqt6")),
    ("qt", ("qt", "qt6", "qt5", "qwidget", "qml")),
    ("tkinter", ("tkinter", "tk")),
    ("customtkinter", ("customtkinter", "custom tkinter")),
    ("kivy", ("kivy",)),
    ("wxpython", ("wxpython", "wx python")),
    ("flutter", ("flutter",)),
    ("react-native", ("react native", "react-native")),
    ("ionic", ("ionic", "capacitor", "cordova")),
    ("android", ("android", "apk", "jetpack compose")),
    ("ios", ("ios", "iphone", "ipad", "swiftui", "uikit")),
    ("unity", ("unity", "unity3d")),
    ("godot", ("godot", "gdscript")),
    ("unreal", ("unreal", "unreal engine", "ue5", "ue4")),
    ("desktop-app", ("desktop app", "desktop application", "desktop gui", "native app", "pyside", "pyside6", "pyqt", "tkinter", "customtkinter", "qt", "electron", "tauri", "wpf", "winforms", "wxwidgets", "wxpython", "gtk", "kivy")),
    ("web-app", ("web app", "web application", "website", "frontend", "front end", "backend", "back end", "full stack", "full-stack", "react", "vue", "svelte", "angular", "django", "flask", "fastapi", "express", "next.js", "nuxt")),
    ("mobile-app", ("mobile app", "mobile application", "android", "ios", "flutter", "react native", "ionic", "capacitor", "cordova")),
    ("game", ("game", "game engine", "unity", "godot", "unreal", "love2d", "pygame", "phaser")),
    ("api", ("api", "rest api", "restful", "graphql", "grpc", "endpoint")),
    ("backend", ("backend", "back end", "server", "api server", "database")),
    ("frontend", ("frontend", "front end", "ui", "ux", "single page app", "spa")),
    ("cli", ("cli", "command line", "command-line", "terminal app", "console app")),
    ("automation", ("automation", "script", "bot", "workflow")),
    ("data", ("data", "dataset", "pandas", "numpy", "jupyter", "etl")),
    ("machine-learning", ("machine learning", "ml", "ai", "neural network", "tensorflow", "pytorch", "scikit-learn", "sklearn")),
    ("database", ("database", "sql", "sqlite", "postgres", "postgresql", "mysql", "mariadb", "mongodb", "redis", "supabase", "firebase")),
    ("devops", ("devops", "docker", "kubernetes", "ci/cd", "github actions", "terraform")),
)
INFERRED_NAME_TAG_STOPWORDS = {
    "app",
    "application",
    "demo",
    "project",
    "tool",
    "tools",
    "new",
    "manager",
    "website",
    "site",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_project_data_path() -> Path:
    return repo_root() / "_data" / "projects.json"


def default_settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / ORG_NAME / "ProjectManager" / "settings.json"
    return Path.home() / ".riffpointer-project-manager" / "settings.json"


def normalize_tag(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def infer_project_tags(name: str, description: str) -> list[str]:
    text = f"{name} {description}".lower()
    tags: list[str] = []
    seen: set[str] = set()
    for tag, phrases in TAG_INFERENCE_RULES:
        if tag in seen:
            continue
        if any(_contains_inference_phrase(text, phrase) for phrase in phrases):
            tags.append(tag)
            seen.add(tag)

    for part in re.split(r"[\s_/.,:;()[\]{}+-]+", name):
        tag = normalize_tag(part)
        if len(tag) >= 3 and tag not in INFERRED_NAME_TAG_STOPWORDS and tag not in seen:
            tags.append(tag)
            seen.add(tag)
    return tags


def _contains_inference_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.lower()
    if any(char in phrase for char in "#+/."):
        return phrase in text
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def title_from_repo_name(name: str) -> str:
    words = [word for word in re.split(r"[-_\s]+", name.strip()) if word]
    return " ".join(word if word.isupper() else word[:1].upper() + word[1:] for word in words) or name


def repositories_to_project_entries(repositories: list[dict[str, Any]], ignore_forks: bool) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for repo in repositories:
        if ignore_forks and _repo_is_fork(repo.get("fork")):
            continue
        repo_name = str(repo.get("name") or "").strip()
        repo_id = str(repo.get("id") or "").strip()
        if not repo_id or repo_id in seen_ids:
            continue
        seen_ids.add(repo_id)
        name = repo_name or title_from_repo_name(repo_id)
        description = str(repo.get("description") or "").strip()
        language = str(repo.get("language") or "").strip()
        tags = infer_project_tags(name, " ".join(part for part in (description, language) if part))
        if language:
            language_tag = normalize_tag(language)
            if language_tag and language_tag not in tags:
                tags.insert(0, language_tag)
        projects.append(
            {
                "name": name,
                "description": description,
                "id": repo_id,
                "has_demo": repo_id.endswith(".github.io"),
                "tags": tags,
            }
        )
    return projects


def _repo_is_fork(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


@dataclass
class SettingsManager:
    bootstrap_path: Path = field(default_factory=default_settings_path)
    settings_path: Path = field(init=False)
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.settings_path = self.bootstrap_path
        self.load()

    def load(self) -> None:
        bootstrap = self._read_json(self.bootstrap_path)
        custom_path = bootstrap.get("settings_file")
        if custom_path:
            self.settings_path = Path(custom_path).expanduser()
        self.values = self._read_json(self.settings_path)
        if "project_data_path" not in self.values:
            self.values["project_data_path"] = str(default_project_data_path())
        if "theme" not in self.values:
            self.values["theme"] = "auto"
        if "compact_mode" not in self.values:
            self.values["compact_mode"] = False
        if "github_owner" not in self.values:
            self.values["github_owner"] = "RiffPointer"
        if "confirm_delete" not in self.values:
            self.values["confirm_delete"] = True

    def save(self) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
        if self.settings_path != self.bootstrap_path:
            self.bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
            self.bootstrap_path.write_text(
                json.dumps({"settings_file": str(self.settings_path)}, indent=2),
                encoding="utf-8",
            )

    def move_settings(self, new_path: Path) -> None:
        new_path = new_path.expanduser().resolve()
        if new_path == self.settings_path.resolve():
            return
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if self.settings_path.exists():
            shutil.copy2(self.settings_path, new_path)
        self.settings_path = new_path
        self.save()

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}


def file_error_message(path: Path, action: str, exc: Exception) -> str:
    if isinstance(exc, FileNotFoundError):
        reason = "The file does not exist."
    elif isinstance(exc, PermissionError):
        reason = "The file is not readable."
    elif isinstance(exc, json.JSONDecodeError):
        reason = f"Invalid JSON at line {exc.lineno}, column {exc.colno}."
    elif isinstance(exc, UnicodeDecodeError):
        reason = "The file is not valid UTF-8 text."
    else:
        reason = str(exc)
    return f"Could not {action}:\n{path}\n\n{reason}"


def read_json_file(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def is_dark_mode_preferred() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(value) == 0
    except OSError:
        return False


def apply_dark_fusion_palette(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)


def apply_light_windows_theme(app: QApplication) -> None:
    available = {style.lower(): style for style in QStyleFactory.keys()}
    style_name = available.get("windowsvista") or available.get("windows")
    if style_name is not None:
        app.setStyle(style_name)
    else:
        app.setStyle("Fusion")
    app.setPalette(QPalette())


def apply_theme(app: QApplication, theme: str) -> None:
    choice = theme.strip().lower()
    if choice == "dark":
        apply_dark_fusion_palette(app)
    elif choice == "light":
        apply_light_windows_theme(app)
    else:
        if is_dark_mode_preferred():
            apply_dark_fusion_palette(app)
        else:
            apply_light_windows_theme(app)


def _fuzzy_match(needle: str, haystack: str) -> bool:
    if not needle:
        return True
    if needle in haystack:
        return True
    tokens = [token for token in re.split(r"\s+", needle) if token]
    if tokens and all(token in haystack for token in tokens):
        return True
    h_index = 0
    matched = 0
    for char in needle:
        pos = haystack.find(char, h_index)
        if pos == -1:
            return False
        matched += 1
        h_index = pos + 1
    return matched >= max(3, len(needle) // 2)


class ProjectsModel(QAbstractTableModel):
    def __init__(self, projects: list[dict[str, Any]] | None = None) -> None:
        super().__init__()
        self.projects = projects or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.projects)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(PROJECT_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        project = self.projects[index.row()]
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if column == 0:
                return project.get("name", "")
            if column == 1:
                return project.get("id", "")
            if column == 2:
                return "Yes" if self._as_bool(project.get("has_demo")) else "No"
            if column == 3:
                tags = project.get("tags", [])
                return ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else str(tags)
            if column == 4:
                return project.get("description", "")
        if role == Qt.ToolTipRole:
            return project.get("description", "")
        if role == Qt.TextAlignmentRole and column == 2:
            return Qt.AlignCenter
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return PROJECT_COLUMNS[section]
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base = super().flags(index)
        return base | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def set_projects(self, projects: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self.projects = projects
        self.endResetModel()

    def add_project(self, project: dict[str, Any]) -> None:
        row = len(self.projects)
        self.beginInsertRows(QModelIndex(), row, row)
        self.projects.append(project)
        self.endInsertRows()

    def insert_project(self, row: int, project: dict[str, Any]) -> None:
        row = max(0, min(row, len(self.projects)))
        self.beginInsertRows(QModelIndex(), row, row)
        self.projects.insert(row, project)
        self.endInsertRows()

    def replace_project(self, row: int, project: dict[str, Any]) -> None:
        self.projects[row] = project
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def remove_project(self, row: int) -> dict[str, Any]:
        self.beginRemoveRows(QModelIndex(), row, row)
        project = self.projects.pop(row)
        self.endRemoveRows()
        return project

    def move_project(self, source_row: int, target_row: int) -> None:
        if source_row == target_row or source_row < 0 or source_row >= len(self.projects):
            return
        target_row = max(0, min(target_row, len(self.projects)))
        if target_row == source_row:
            return
        if target_row > source_row:
            target_row += 1
        self.beginMoveRows(QModelIndex(), source_row, source_row, QModelIndex(), target_row)
        project = self.projects.pop(source_row)
        if target_row > source_row:
            target_row -= 1
        self.projects.insert(target_row, project)
        self.endMoveRows()

    @staticmethod
    def _as_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "y", "on"}
        return bool(value)


class ProjectsProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.window: "MainWindow | None" = None
        self._search_text = ""
        self._filter_mode = "fuzzy"
        self.setDynamicSortFilter(False)

    def set_search_text(self, text: str) -> None:
        self._search_text = text.strip()
        self.invalidateRowsFilter()

    def set_filter_mode(self, mode: str) -> None:
        self._filter_mode = mode
        self.invalidateRowsFilter()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        else:
            flags |= Qt.ItemIsDropEnabled
        return flags

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.MoveAction

    def supportedDragActions(self) -> Qt.DropAction:
        return Qt.MoveAction

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_value = self.sourceModel().data(left, Qt.DisplayRole) if self.sourceModel() is not None else None
        right_value = self.sourceModel().data(right, Qt.DisplayRole) if self.sourceModel() is not None else None
        left_column = left.column()
        if left_column == 2:
            return self._display_to_bool(left_value) < self._display_to_bool(right_value)
        return str(left_value).casefold() < str(right_value).casefold()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._search_text:
            return True
        model = self.sourceModel()
        if model is None:
            return True
        haystack_parts: list[str] = []
        for column in range(model.columnCount()):
            index = model.index(source_row, column, source_parent)
            value = model.data(index, Qt.DisplayRole)
            if value is not None:
                haystack_parts.append(str(value))
        haystack = " ".join(haystack_parts).casefold()
        needle = self._search_text.casefold()
        if self._filter_mode == "exact":
            return needle in haystack
        if self._filter_mode == "all":
            return all(token in haystack for token in needle.split())
        if self._filter_mode == "prefix":
            return any(part.casefold().startswith(needle) for part in haystack_parts)
        return _fuzzy_match(needle, haystack)

    @staticmethod
    def _display_to_bool(value: Any) -> bool:
        return str(value).strip().casefold() == "yes"

    def mimeTypes(self) -> list[str]:
        return ["application/x-riffpointer-project-row"]

    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        mime = QMimeData()
        rows = sorted({index.row() for index in indexes if index.isValid()})
        if rows:
            mime.setData("application/x-riffpointer-project-row", ",".join(map(str, rows)).encode("utf-8"))
        return mime

    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        if action != Qt.MoveAction or not data.hasFormat("application/x-riffpointer-project-row"):
            return False
        if self.window is None:
            return False
        try:
            payload = bytes(data.data("application/x-riffpointer-project-row")).decode("utf-8")
            source_rows = [int(value) for value in payload.split(",") if value.strip()]
        except ValueError:
            return False
        if not source_rows:
            return False
        source_row = source_rows[0]
        if row < 0:
            if parent.isValid():
                row = parent.row()
            else:
                row = self.rowCount()
        target_row = row
        source_model = self.sourceModel()
        if source_model is None:
            return False
        source_index = self.mapToSource(self.index(source_row, 0))
        if not source_index.isValid():
            return False
        actual_source_row = source_index.row()
        target_source_row = target_row
        if target_row < self.rowCount():
            target_index = self.mapToSource(self.index(target_row, 0))
            if target_index.isValid():
                target_source_row = target_index.row()
        if self.window.project_order_move_is_noop(actual_source_row, target_source_row):
            return False
        self.window.undo_stack.push(ReorderProjectsCommand(self.window, actual_source_row, target_source_row))
        self.window.mark_dirty("Project order changed")
        self.window.autosave_projects("Project order changed and saved")
        return True


class EditProjectCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", row: int, before: dict[str, Any], after: dict[str, Any]) -> None:
        super().__init__(f"Edit {before.get('name', 'Project')}")
        self.window = window
        self.row = row
        self.before = before
        self.after = after

    def undo(self) -> None:
        self.window.model.replace_project(self.row, self.before)

    def redo(self) -> None:
        self.window.model.replace_project(self.row, self.after)


class AddProjectCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", project: dict[str, Any]) -> None:
        super().__init__(f"Add {project.get('name', 'Project')}")
        self.window = window
        self.project = project
        self.row = len(window.model.projects)
        self._inserted = False

    def undo(self) -> None:
        self.window.model.remove_project(self.row)
        self._inserted = False

    def redo(self) -> None:
        if not self._inserted:
            self.window.model.insert_project(self.row, self.project)
            self._inserted = True
            return
        self.window.model.insert_project(self.row, self.project)


class AddProjectsCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", projects: list[dict[str, Any]]) -> None:
        super().__init__(f"Add {len(projects)} Projects")
        self.window = window
        self.projects = projects
        self.row = len(window.model.projects)
        self._inserted = False

    def undo(self) -> None:
        for _project in self.projects:
            self.window.model.remove_project(self.row)
        self._inserted = False

    def redo(self) -> None:
        for offset, project in enumerate(self.projects):
            self.window.model.insert_project(self.row + offset, project)
        self._inserted = True


class DeleteProjectCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", row: int, project: dict[str, Any]) -> None:
        super().__init__(f"Delete {project.get('name', 'Project')}")
        self.window = window
        self.row = row
        self.project = project
        self._removed = False

    def undo(self) -> None:
        self.window.model.insert_project(self.row, self.project)
        self._removed = False

    def redo(self) -> None:
        if not self._removed:
            self.window.model.remove_project(self.row)
            self._removed = True
            return
        self.window.model.remove_project(self.row)


class DeleteProjectsCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", rows: list[int]) -> None:
        self.rows = sorted(set(rows))
        self.projects = [dict(window.model.projects[row]) for row in self.rows]
        super().__init__(f"Delete {len(self.rows)} Projects")
        self.window = window

    def undo(self) -> None:
        for row, project in zip(self.rows, self.projects):
            self.window.model.insert_project(row, project)

    def redo(self) -> None:
        for row in reversed(self.rows):
            self.window.model.remove_project(row)


class DuplicateProjectCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", row: int, project: dict[str, Any]) -> None:
        super().__init__(f"Duplicate {project.get('name', 'Project')}")
        self.window = window
        self.row = row
        self.project = project
        self._inserted = False

    def undo(self) -> None:
        self.window.model.remove_project(self.row)
        self._inserted = False

    def redo(self) -> None:
        if not self._inserted:
            self.window.model.insert_project(self.row, self.project)
            self._inserted = True
            return
        self.window.model.insert_project(self.row, self.project)


class MagicNamesCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", rows: list[int]) -> None:
        self.rows = list(rows)
        self.before = [dict(window.model.projects[row]) for row in self.rows]
        self.after = []
        for project in self.before:
            updated = dict(project)
            project_id = str(project.get("id", "")).strip()
            if project_id:
                updated["name"] = ProjectDialog._magic_name_from_id(project_id)
            self.after.append(updated)
        super().__init__(f"Apply Magic to {len(self.rows)} Names")
        self.window = window

    def undo(self) -> None:
        for row, project in zip(self.rows, self.before):
            self.window.model.replace_project(row, project)

    def redo(self) -> None:
        for row, project in zip(self.rows, self.after):
            self.window.model.replace_project(row, project)


class ReorderProjectsCommand(QUndoCommand):
    def __init__(self, window: "MainWindow", source_row: int, target_row: int) -> None:
        super().__init__("Reorder Projects")
        self.window = window
        self.before = [dict(project) for project in window.model.projects]
        self.after = self._reordered_list(self.before, source_row, target_row)

    @staticmethod
    def _reordered_list(projects: list[dict[str, Any]], source_row: int, target_row: int) -> list[dict[str, Any]]:
        reordered = list(projects)
        if source_row < 0 or source_row >= len(reordered):
            return reordered
        project = reordered.pop(source_row)
        if target_row < 0:
            target_row = 0
        if target_row > len(reordered):
            target_row = len(reordered)
        reordered.insert(target_row, project)
        return reordered

    def undo(self) -> None:
        self.window.model.set_projects([dict(project) for project in self.before])

    def redo(self) -> None:
        self.window.model.set_projects([dict(project) for project in self.after])


class ProjectDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, project: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Project" if project else "New Project")
        self.setMinimumWidth(560)
        self._id_touched = False
        self._generated_id = ""
        self._tags_touched = project is not None
        self._generated_tags = ""

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Project name")
        self.magic_button = QPushButton("Magic")
        self.magic_button.setToolTip("Generate a human-readable project name from the ID")
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("unique-project-id")
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(110)
        self.description_edit.setPlaceholderText("Short project summary")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("tag-one, tag-two, tag-three")
        self.demo_check = QCheckBox("Project has a demo page")

        name_row = QHBoxLayout()
        name_row.addWidget(self.name_edit, 1)
        name_row.addWidget(self.magic_button)

        form = QFormLayout()
        form.addRow("Name", name_row)
        form.addRow("ID", self.id_edit)
        form.addRow("Description", self.description_edit)
        form.addRow("Tags", self.tags_edit)
        form.addRow("", self.demo_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.name_edit.textChanged.connect(self._suggest_id_from_name)
        self.name_edit.textChanged.connect(self._suggest_tags_from_text)
        self.description_edit.textChanged.connect(self._suggest_tags_from_text)
        self.magic_button.clicked.connect(self._apply_magic_name)
        self.id_edit.textEdited.connect(self._mark_id_touched)
        self.tags_edit.textEdited.connect(self._mark_tags_touched)

        if project:
            self._id_touched = True
            self._generated_id = str(project.get("id", "")).strip()
            self.name_edit.setText(str(project.get("name", "")))
            self.id_edit.setText(str(project.get("id", "")))
            self.description_edit.setPlainText(str(project.get("description", "")))
            tags = project.get("tags", [])
            self.tags_edit.setText(", ".join(tags) if isinstance(tags, list) else str(tags))
            self.demo_check.setChecked(ProjectsModel._as_bool(project.get("has_demo")))

    def accept(self) -> None:
        if not self.name_edit.text().strip() or not self.id_edit.text().strip():
            QMessageBox.warning(self, "Missing Project Data", "Name and ID are required.")
            return
        super().accept()

    def project(self) -> dict[str, Any]:
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "id": self.id_edit.text().strip(),
            "has_demo": self.demo_check.isChecked(),
            "tags": tags,
        }

    def _mark_id_touched(self) -> None:
        self._id_touched = True

    def _mark_tags_touched(self) -> None:
        self._tags_touched = True

    def _suggest_id_from_name(self, text: str) -> None:
        if self._id_touched:
            return
        current = self.id_edit.text().strip()
        if not text.strip():
            if current == self._generated_id:
                self._generated_id = ""
                self.id_edit.clear()
            return
        normalized = text.strip().lower().replace("'", "")
        slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
        if current and current != self._generated_id:
            return
        if slug and slug != current:
            self._generated_id = slug
            self.id_edit.setText(slug)
        elif not slug and current == self._generated_id:
            self._generated_id = ""
            self.id_edit.clear()

    def _suggest_tags_from_text(self, *_args: object) -> None:
        if self._tags_touched:
            return
        current = self.tags_edit.text().strip()
        if current and current != self._generated_tags:
            self._tags_touched = True
            return

        inferred = infer_project_tags(self.name_edit.text(), self.description_edit.toPlainText())
        tags = ", ".join(inferred)
        if tags == current:
            return
        self._generated_tags = tags
        self.tags_edit.setText(tags)

    def _apply_magic_name(self) -> None:
        source = self.id_edit.text().strip()
        if not source:
            return
        self.name_edit.setText(self._magic_name_from_id(source))
        self._generated_id = self.id_edit.text().strip()
        self._generated_tags = self.tags_edit.text().strip()

    @staticmethod
    def _magic_name_from_id(project_id: str) -> str:
        raw_tokens = [token for token in re.split(r"[-_\s]+", project_id.strip()) if token]
        tokens: list[str] = []
        for token in raw_tokens:
            parts = [part for part in re.split(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", token) if part]
            tokens.extend(parts or [token])
        if not tokens:
            return project_id

        first = tokens[0].strip()
        rest = tokens[1:]
        if first.casefold() == "riffpointers" and rest[:1] == ["hub"]:
            return "RiffPointer's Hub"

        words: list[str] = []
        for token in tokens:
            if token.isupper():
                words.append(token)
            else:
                words.append(token[:1].upper() + token[1:].lower())
        return " ".join(words)


class AutocrawlerDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Autocrawler")
        self.setMinimumWidth(420)

        self.username_edit = QLineEdit(DEFAULT_GITHUB_OWNER)
        self.username_edit.setPlaceholderText("github username")
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Web crawler", GITHUB_WEB_MODE)
        self.mode_combo.addItem("GitHub API", GITHUB_API_MODE)
        self.ignore_forks_check = QCheckBox("Ignore forked repositories")
        self.ignore_forks_check.setChecked(True)

        form = QFormLayout()
        form.addRow("GitHub username", self.username_edit)
        form.addRow("Extraction mode", self.mode_combo)
        form.addRow("", self.ignore_forks_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self) -> None:
        if not self.username().strip():
            QMessageBox.warning(self, "Missing Username", "GitHub username is required.")
            return
        super().accept()

    def username(self) -> str:
        return self.username_edit.text().strip().strip("/")

    def ignore_forks(self) -> bool:
        return self.ignore_forks_check.isChecked()

    def extraction_mode(self) -> str:
        return str(self.mode_combo.currentData() or GITHUB_WEB_MODE)


class PreferencesDialog(QDialog):
    def __init__(self, settings: SettingsManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(660)

        self.project_path_edit = QLineEdit(str(settings.values.get("project_data_path", default_project_data_path())))
        self.settings_path_edit = QLineEdit(str(settings.settings_path))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Light", "Dark"])
        current_theme = str(settings.values.get("theme", "auto")).lower()
        self.theme_combo.setCurrentIndex(THEME_OPTIONS.index(current_theme) if current_theme in THEME_OPTIONS else 0)
        self.github_owner_edit = QLineEdit(str(settings.values.get("github_owner", "RiffPointer")))
        self.compact_check = QCheckBox("Compact mode for smaller screens")
        self.compact_check.setChecked(bool(settings.values.get("compact_mode", False)))
        self.confirm_delete_check = QCheckBox("Show delete confirmation")
        self.confirm_delete_check.setChecked(bool(settings.values.get("confirm_delete", True)))

        project_browse = QPushButton("Browse...")
        project_browse.clicked.connect(self.choose_project_file)
        settings_browse = QPushButton("Browse...")
        settings_browse.clicked.connect(self.choose_settings_file)

        project_row = QHBoxLayout()
        project_row.addWidget(self.project_path_edit, 1)
        project_row.addWidget(project_browse)

        settings_row = QHBoxLayout()
        settings_row.addWidget(self.settings_path_edit, 1)
        settings_row.addWidget(settings_browse)

        theme_row = QHBoxLayout()
        theme_row.addWidget(self.theme_combo, 1)

        form = QFormLayout()
        form.addRow("Project data file", project_row)
        form.addRow("Settings storage file", settings_row)
        form.addRow("GitHub owner", self.github_owner_edit)
        form.addRow("Theme", theme_row)
        form.addRow("", self.compact_check)
        form.addRow("", self.confirm_delete_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def choose_project_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose Project Data", self.project_path_edit.text(), "JSON files (*.json);;All files (*.*)")
        if path:
            self.project_path_edit.setText(path)

    def choose_settings_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Choose Settings Storage", self.settings_path_edit.text(), "JSON files (*.json);;All files (*.*)")
        if path:
            self.settings_path_edit.setText(path)

    def accept(self) -> None:
        project_path = Path(self.project_path_edit.text()).expanduser()
        settings_path = Path(self.settings_path_edit.text()).expanduser()
        if not project_path.exists():
            QMessageBox.warning(self, "Project Data Missing", "The selected project data file does not exist.")
            return
        self.settings.values["project_data_path"] = str(project_path.resolve())
        self.settings.values["github_owner"] = self.github_owner_edit.text().strip() or "RiffPointer"
        self.settings.values["theme"] = THEME_OPTIONS[self.theme_combo.currentIndex()]
        self.settings.values["compact_mode"] = self.compact_check.isChecked()
        self.settings.values["confirm_delete"] = self.confirm_delete_check.isChecked()
        self.settings.move_settings(settings_path)
        self.settings.save()
        super().accept()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsManager()
        self.data_path = Path(self.settings.values["project_data_path"]).expanduser()
        self._data_signature: tuple[int, int] | None = None
        self.dirty = False
        self.undo_stack = QUndoStack(self)
        self.undo_stack.indexChanged.connect(self._sync_dirty_state)

        self.setWindowTitle(APP_NAME)
        self.resize(1080, 680)

        self.model = ProjectsModel()
        self.model.modelReset.connect(self.update_empty_state)
        self.model.rowsInserted.connect(self.update_empty_state)
        self.model.rowsRemoved.connect(self.update_empty_state)
        self.proxy = ProjectsProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.proxy.window = self

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setDefaultDropAction(Qt.MoveAction)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.edit_selected_project)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        self.table.selectionModel().selectionChanged.connect(self._sync_selection_actions)
        self.table.viewport().installEventFilter(self)
        self.setAcceptDrops(True)
        self.empty_label = QLabel("No projects")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #808080; font-size: 18px;")
        self.empty_label.setWordWrap(True)
        self.central_stack = QStackedWidget()
        self.central_stack.addWidget(self.table)
        self.central_stack.addWidget(self.empty_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search projects...")
        self.search_edit.textChanged.connect(self.proxy.set_search_text)
        self.filter_button = QToolButton()
        self.filter_button.setText("Filter")
        self.filter_button.setPopupMode(QToolButton.InstantPopup)
        self.filter_button.setToolTip("Search filter options")
        self._build_filter_menu()

        top = QToolBar("Quick Actions")
        top.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, top)
        self._build_actions()
        top.addWidget(self.search_edit)
        top.addWidget(self.filter_button)
        top.addAction(self.undo_action)
        top.addAction(self.redo_action)
        top.addSeparator()
        top.addAction(self.new_action)
        top.addAction(self.edit_action)
        top.addAction(self.delete_action)
        top.addSeparator()
        top.addAction(self.save_action)
        top.addAction(self.reload_action)

        self.setCentralWidget(self.central_stack)
        self.setStatusBar(QStatusBar())
        self._build_menus()
        self.apply_compact_mode(bool(self.settings.values.get("compact_mode", False)))
        self.load_projects()
        self._sync_selection_actions()

    def _build_actions(self) -> None:
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_project)

        self.undo_action = self.undo_stack.createUndoAction(self, "Undo")
        self.undo_action.setShortcut(QKeySequence.Undo)

        self.redo_action = self.undo_stack.createRedoAction(self, "Redo")
        self.redo_action.setShortcut(QKeySequence.Redo)

        self.edit_action = QAction("Edit", self)
        self.edit_action.setShortcut(QKeySequence("Ctrl+E"))
        self.edit_action.triggered.connect(self.edit_selected_project)

        self.duplicate_action = QAction("Duplicate", self)
        self.duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        self.duplicate_action.triggered.connect(self.duplicate_selected_project)

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.delete_selected_project)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_projects)

        self.reload_action = QAction("Reload", self)
        self.reload_action.setShortcut(QKeySequence.Refresh)
        self.reload_action.triggered.connect(self.reload_projects)

        self.manual_ordering_action = QAction("Manual Ordering", self, checkable=True)
        self.manual_ordering_action.setChecked(True)
        self.manual_ordering_action.toggled.connect(self.toggle_manual_ordering)

        self.preferences_action = QAction("Preferences...", self)
        self.preferences_action.triggered.connect(self.open_preferences)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)

    def _build_filter_menu(self) -> None:
        menu = QMenu(self)
        self.filter_mode_group = []
        for label, mode in (
            ("Fuzzy Match", "fuzzy"),
            ("Contains All Words", "all"),
            ("Contains Any Text", "exact"),
            ("Prefix Match", "prefix"),
        ):
            action = QAction(label, self, checkable=True)
            action.setData(mode)
            action.triggered.connect(lambda checked=False, m=mode: self.set_search_filter_mode(m))
            menu.addAction(action)
            self.filter_mode_group.append(action)
        menu.addSeparator()
        menu.addAction("Clear Search", self.search_edit.clear)
        self.filter_button.setMenu(menu)
        self.set_search_filter_mode("fuzzy")

    def set_search_filter_mode(self, mode: str) -> None:
        self.proxy.set_filter_mode(mode)
        for action in getattr(self, "filter_mode_group", []):
            action.blockSignals(True)
            action.setChecked(action.data() == mode)
            action.blockSignals(False)
        labels = {
            "fuzzy": "Filter: Fuzzy",
            "all": "Filter: All Words",
            "exact": "Filter: Contains",
            "prefix": "Filter: Prefix",
        }
        self.filter_button.setText(labels.get(mode, "Filter"))

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.reload_action)
        file_menu.addSeparator()
        file_menu.addAction(self.preferences_action)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close, QKeySequence.Quit)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.edit_action)
        edit_menu.addAction(self.duplicate_action)
        edit_menu.addAction(self.delete_action)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction("Clear Search", self.search_edit.clear)
        view_menu.addAction(self.manual_ordering_action)
        view_menu.addSeparator()
        columns_menu = view_menu.addMenu("Columns")
        self.column_visibility_actions = []
        for column, title in enumerate(PROJECT_COLUMNS):
            action = QAction(title, self, checkable=True)
            action.setChecked(True)
            action.toggled.connect(lambda checked, col=column: self.set_column_visible(col, checked))
            self.column_visibility_actions.append(action)
            columns_menu.addAction(action)

        view_menu.addAction("Show All Columns", self.show_all_columns)
        view_menu.addAction("Hide All Columns", self.hide_all_columns)

        tools_menu = self.menuBar().addMenu("&Tools")
        tools_menu.addAction("Format &Validate JSON", self.format_validate_json)
        tools_menu.addAction("Check Links", self.check_links)
        tools_menu.addSeparator()
        tools_menu.addAction("Apply Magic to Names", self.apply_magic_to_selected_names)
        tools_menu.addAction("Autocrawler", self.autocrawl_github_repositories)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.about_action)

    def load_projects(self) -> None:
        try:
            data = load_json(self.data_path)
            if not isinstance(data, list):
                raise TypeError("Project data must be a JSON array of project objects.")
        except FileNotFoundError as exc:
            QMessageBox.critical(self, "Unable to Load Projects", file_error_message(self.data_path, "load the project list", exc))
            self.model.set_projects([])
            self.undo_stack.clear()
            self.dirty = False
            self._data_signature = None
            self.statusBar().showMessage(f"Load failed for {self.data_path}", 6000)
            return
        except PermissionError as exc:
            QMessageBox.critical(self, "Unable to Load Projects", file_error_message(self.data_path, "load the project list", exc))
            self.model.set_projects([])
            self.undo_stack.clear()
            self.dirty = False
            self._data_signature = None
            self.statusBar().showMessage(f"Load failed for {self.data_path}", 6000)
            return
        except UnicodeDecodeError as exc:
            QMessageBox.critical(self, "Unable to Load Projects", file_error_message(self.data_path, "load the project list", exc))
            self.model.set_projects([])
            self.undo_stack.clear()
            self.dirty = False
            self._data_signature = None
            self.statusBar().showMessage(f"Load failed for {self.data_path}", 6000)
            return
        except json.JSONDecodeError as exc:
            QMessageBox.critical(self, "Unable to Load Projects", file_error_message(self.data_path, "load the project list", exc))
            self.model.set_projects([])
            self.undo_stack.clear()
            self.dirty = False
            self._data_signature = None
            self.statusBar().showMessage(f"Load failed for {self.data_path}", 6000)
            return
        except (TypeError, ValueError, OSError) as exc:
            QMessageBox.critical(self, "Unable to Load Projects", file_error_message(self.data_path, "load the project list", exc))
            self.model.set_projects([])
            self.undo_stack.clear()
            self.dirty = False
            self._data_signature = None
            self.statusBar().showMessage(f"Load failed for {self.data_path}", 6000)
            return
        self.model.set_projects(data)
        self.undo_stack.clear()
        self.dirty = False
        self._data_signature = self._stat_signature(self.data_path)
        self.statusBar().showMessage(f"Loaded {len(data)} projects from {self.data_path}", 6000)
        self._sync_column_visibility_actions()
        self._sync_manual_ordering_state()

    def project_id_exists(self, project_id: str, ignore_row: int | None = None) -> bool:
        needle = project_id.strip().casefold()
        for row, project in enumerate(self.model.projects):
            if ignore_row is not None and row == ignore_row:
                continue
            if str(project.get("id", "")).strip().casefold() == needle:
                return True
        return False

    def warn_duplicate_project_id(self, project_id: str) -> None:
        QMessageBox.warning(
            self,
            "Duplicate Project ID",
            f"The project ID '{project_id}' is already in use. Use a unique ID.",
        )

    def project_order_move_is_noop(self, source_row: int, target_row: int) -> bool:
        return source_row == target_row or source_row < 0 or target_row < 0 or source_row >= len(self.model.projects)

    def toggle_manual_ordering(self, enabled: bool) -> None:
        if enabled:
            self.table.setDragDropMode(QAbstractItemView.DragDrop)
        else:
            self.table.setDragDropMode(QAbstractItemView.NoDragDrop)
        self._sync_manual_ordering_state()

    def _sync_manual_ordering_state(self) -> None:
        action = getattr(self, "manual_ordering_action", None)
        if action is not None:
            action.blockSignals(True)
            action.setChecked(self.table.dragDropMode() == QAbstractItemView.DragDrop)
            action.blockSignals(False)

    def set_column_visible(self, column: int, visible: bool) -> None:
        self.table.setColumnHidden(column, not visible)
        self._sync_column_visibility_actions()

    def show_all_columns(self) -> None:
        for column in range(len(PROJECT_COLUMNS)):
            self.table.setColumnHidden(column, False)
        self._sync_column_visibility_actions()

    def hide_all_columns(self) -> None:
        for column in range(len(PROJECT_COLUMNS)):
            self.table.setColumnHidden(column, True)
        self._sync_column_visibility_actions()

    def _sync_column_visibility_actions(self) -> None:
        for column, action in enumerate(getattr(self, "column_visibility_actions", [])):
            action.blockSignals(True)
            action.setChecked(not self.table.isColumnHidden(column))
            action.blockSignals(False)

    def _sync_selection_actions(self) -> None:
        selected_count = len(self.selected_source_rows())
        single_selection = selected_count == 1
        for action in (getattr(self, "edit_action", None), getattr(self, "duplicate_action", None)):
            if action is not None:
                action.setEnabled(single_selection)
        delete_action = getattr(self, "delete_action", None)
        if delete_action is not None:
            delete_action.setEnabled(selected_count > 0)

    def update_empty_state(self) -> None:
        if not hasattr(self, "central_stack"):
            return
        self.central_stack.setCurrentWidget(self.empty_label if not self.model.projects else self.table)

    def eventFilter(self, watched, event) -> bool:
        if watched in {self, self.table.viewport()}:
            if event.type() == QEvent.DragEnter and self._event_has_folder_urls(event):
                event.acceptProposedAction()
                return True
            if event.type() == QEvent.Drop and self._event_has_folder_urls(event):
                folder = self._first_dropped_folder(event)
                if folder is not None:
                    self.import_project_folder(folder)
                    event.acceptProposedAction()
                    return True
        return super().eventFilter(watched, event)

    @staticmethod
    def _event_has_folder_urls(event) -> bool:
        mime = event.mimeData()
        return bool(mime and mime.hasUrls())

    @staticmethod
    def _first_dropped_folder(event) -> Path | None:
        mime = event.mimeData()
        if mime is None:
            return None
        for url in mime.urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if path.is_dir():
                return path
        return None

    def import_project_folder(self, folder: Path) -> None:
        progress = QProgressDialog("Scanning project folder...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Import Project")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.show()

        def report(value: int, message: str) -> None:
            progress.setLabelText(message)
            progress.setValue(value)
            QApplication.processEvents()

        try:
            result = scan_project_folder(folder, report, lambda: progress.wasCanceled())
        except RuntimeError:
            progress.close()
            self.statusBar().showMessage("Project import canceled", 4000)
            return
        finally:
            progress.close()

        project = result.project
        base_id = str(project.get("id", "project")).strip() or "project"
        project_id = base_id
        suffix = 2
        while self.project_id_exists(project_id):
            project_id = f"{base_id}-{suffix}"
            suffix += 1
        project["id"] = project_id

        self.undo_stack.push(AddProjectCommand(self, project))
        self.mark_dirty("Project imported")
        self.autosave_projects(
            f"Imported {project.get('name', folder.name)} from folder scan"
        )

    def autocrawl_github_repositories(self) -> None:
        settings_dialog = AutocrawlerDialog(self)
        if settings_dialog.exec() != QDialog.Accepted:
            return

        username = settings_dialog.username()
        ignore_forks = settings_dialog.ignore_forks()
        extraction_mode = settings_dialog.extraction_mode()
        crawl_url = github_repositories_api_url(username) if extraction_mode == GITHUB_API_MODE else github_repositories_url(username)

        progress = QProgressDialog("Preparing GitHub autocrawler...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Autocrawler")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumWidth(720)
        progress.resize(720, 150)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()

        def report(value: int, message: str) -> bool:
            progress.setLabelText(f"{message}\n{crawl_url}")
            progress.setValue(value)
            QApplication.processEvents()
            return progress.wasCanceled()

        try:
            repositories = fetch_github_repositories(username, extraction_mode, report)
            if report(92, "Converting repositories to project entries..."):
                raise RuntimeError("Autocrawler canceled")
            projects = repositories_to_project_entries(repositories, ignore_forks)
            report(94, f"Prepared {len(projects)} project entries...")
        except RuntimeError:
            progress.close()
            self.statusBar().showMessage("Autocrawler canceled", 5000)
            return
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            progress.close()
            QMessageBox.critical(
                self,
                "Autocrawler Failed",
                f"Could not crawl {crawl_url}\n\n{exc}",
            )
            self.statusBar().showMessage("Autocrawler failed", 5000)
            return

        report(96, "Filtering repositories already present in the project list...")
        existing_ids = {str(project.get("id", "")).strip().casefold() for project in self.model.projects}
        new_projects = [project for project in projects if str(project.get("id", "")).strip().casefold() not in existing_ids]
        skipped = len(projects) - len(new_projects)
        if not new_projects:
            progress.close()
            QMessageBox.information(
                self,
                "Autocrawler",
                f"Found {len(projects)} repositories, but none were new."
                + (f"\nSkipped {skipped} existing project(s)." if skipped else ""),
            )
            self.statusBar().showMessage("Autocrawler found no new projects", 5000)
            return

        report(98, f"Importing {len(new_projects)} new project entries...")
        self.undo_stack.push(AddProjectsCommand(self, new_projects))
        self.mark_dirty("Projects imported by autocrawler")
        self.autosave_projects(
            f"Autocrawler imported {len(new_projects)} project(s)"
            + (f"; skipped {skipped} existing" if skipped else "")
        )
        report(100, "Autocrawler import complete.")
        progress.close()
        QMessageBox.information(
            self,
            "Autocrawler",
            f"Imported {len(new_projects)} project(s) from {crawl_url}."
            + (f"\nSkipped {skipped} existing project(s)." if skipped else ""),
        )

    def format_validate_json(self) -> None:
        try:
            data = load_json(self.data_path)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            QMessageBox.critical(self, "JSON Maintenance", file_error_message(self.data_path, "load the JSON file", exc))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("JSON Maintenance")
        dialog.setMinimumWidth(620)

        summary = QLabel("Running JSON maintenance operations...")
        summary.setWordWrap(True)
        steps = QListWidget()
        save_status = QLabel("Waiting to save...")
        save_status.setWordWrap(True)

        layout = QVBoxLayout(dialog)
        layout.addWidget(summary)
        layout.addWidget(steps)
        layout.addWidget(save_status)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        operation_names = [
            "Sort keys consistently",
            "Pretty-print JSON",
            "Validate schema",
            "Detect missing fields",
        ]
        items: list[QListWidgetItem] = []
        for name in operation_names:
            item = QListWidgetItem(f"{name}: pending")
            steps.addItem(item)
            items.append(item)

        def mark(step_index: int, status: str) -> None:
            items[step_index].setText(f"{operation_names[step_index]}: {status}")
            QApplication.processEvents()

        try:
            mark(0, "running")
            result = format_and_validate_projects(data)
            mark(0, "done")

            mark(1, "running")
            pretty = dump_pretty_sorted_json(result.normalized_data)
            mark(1, "done")

            mark(2, "running" if result.schema_valid else "done with issues")
            mark(3, "running" if result.missing_fields else "done")
        except Exception as exc:
            QMessageBox.critical(self, "JSON Maintenance", f"Could not process JSON:\n\n{exc}")
            return

        if result.missing_fields:
            for field_message in result.missing_fields:
                steps.addItem(QListWidgetItem(f"Missing field: {field_message}"))
        else:
            steps.addItem(QListWidgetItem("Missing field check: none"))

        if result.rule_issues:
            for issue in result.rule_issues:
                steps.addItem(QListWidgetItem(f"Rule issue: {issue}"))
        else:
            steps.addItem(QListWidgetItem("Smart validation rules: passed"))

        if result.schema_valid:
            save_status.setText("Schema validation passed.")
        else:
            save_status.setText("Schema validation found issues.")

        dialog.show()
        QApplication.processEvents()
        if not result.schema_valid:
            save_status.setText("Schema validation failed. Fix the listed issues before saving.")
            dialog.exec()
            return

        try:
            self.data_path.write_text(pretty, encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "JSON Maintenance", file_error_message(self.data_path, "save the JSON file", exc))
            return

        self.load_projects()
        dialog.accept()
        QMessageBox.information(self, "JSON Maintenance", f"Formatted and saved {self.data_path}")

    def apply_compact_mode(self, enabled: bool) -> None:
        header = self.table.horizontalHeader()
        if enabled:
            self.table.setIconSize(self.table.iconSize().boundedTo(self.table.iconSize()))
            self.table.verticalHeader().setDefaultSectionSize(COMPACT_ROW_HEIGHT)
            header.setMinimumHeight(COMPACT_HEADER_HEIGHT)
            header.setFixedHeight(COMPACT_HEADER_HEIGHT)
            self.table.setWordWrap(False)
            self.table.setTextElideMode(Qt.ElideRight)
        else:
            self.table.verticalHeader().setDefaultSectionSize(DEFAULT_ROW_HEIGHT)
            header.setMinimumHeight(DEFAULT_HEADER_HEIGHT)
            header.setFixedHeight(DEFAULT_HEADER_HEIGHT)
            self.table.setWordWrap(False)
            self.table.setTextElideMode(Qt.ElideRight)

    def save_projects(self) -> bool:
        conflict = self._maybe_handle_external_change("save the project list")
        if conflict == "cancel":
            return False
        if conflict == "reload":
            return False
        if conflict == "merge":
            self._merge_external_projects_into_model()
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(self.model.projects, indent=2, ensure_ascii=False)
            self.data_path.write_text(payload + "\n", encoding="utf-8")
        except (TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Unable to Save Projects", f"Could not save the project list:\n{self.data_path}\n\nThe project data contains values that cannot be serialized to JSON.\n\n{exc}")
            return False
        except OSError as exc:
            QMessageBox.critical(self, "Unable to Save Projects", file_error_message(self.data_path, "save the project list", exc))
            return False
        self.undo_stack.setClean()
        self._sync_dirty_state()
        self._data_signature = self._stat_signature(self.data_path)
        self.statusBar().showMessage(f"Saved {len(self.model.projects)} projects", 6000)
        return True

    def autosave_projects(self, status_message: str) -> None:
        if self.save_projects():
            self.statusBar().showMessage(status_message, 5000)

    def reload_projects(self) -> None:
        if not self.confirm_discard_changes():
            return
        self.load_projects()

    def _stat_signature(self, path: Path) -> tuple[int, int] | None:
        try:
            stat = path.stat()
        except OSError:
            return None
        return stat.st_mtime_ns, stat.st_size

    def _has_external_change(self) -> bool:
        current = self._stat_signature(self.data_path)
        return current is not None and self._data_signature is not None and current != self._data_signature

    def _maybe_handle_external_change(self, action: str) -> str | None:
        if not self._has_external_change():
            return None
        box = QMessageBox(self)
        box.setWindowTitle("File Changed Externally")
        box.setIcon(QMessageBox.Warning)
        box.setText("The JSON file changed on disk while this app was open.")
        box.setInformativeText("Reload discards in-memory changes. Merge combines disk changes with your current edits. Overwrite keeps your current data.")
        reload_button = box.addButton("Reload", QMessageBox.AcceptRole)
        merge_button = box.addButton("Merge", QMessageBox.ActionRole)
        overwrite_button = box.addButton("Overwrite", QMessageBox.DestructiveRole)
        cancel_button = box.addButton(QMessageBox.Cancel)
        box.exec()
        clicked = box.clickedButton()
        if clicked == reload_button:
            self.load_projects()
            return "reload"
        if clicked == merge_button:
            return "merge"
        if clicked == overwrite_button:
            return "overwrite"
        return "cancel"

    def _merge_external_projects_into_model(self) -> None:
        try:
            disk_projects = load_json(self.data_path)
        except Exception as exc:
            QMessageBox.critical(self, "Merge Failed", file_error_message(self.data_path, "load the project list", exc))
            return
        if not isinstance(disk_projects, list):
            QMessageBox.warning(self, "Merge Failed", "The on-disk JSON is not a project list.")
            return
        merged: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        def project_key(project: dict[str, Any], fallback: int) -> str:
            value = str(project.get("id", "")).strip().casefold()
            return value or f"__index_{fallback}"

        for index, project in enumerate(disk_projects):
            if not isinstance(project, dict):
                continue
            key = project_key(project, index)
            merged.append(dict(project))
            seen_ids.add(key)

        for index, project in enumerate(self.model.projects):
            if not isinstance(project, dict):
                continue
            key = project_key(project, index)
            replacement = dict(project)
            if key in seen_ids:
                for position, existing in enumerate(merged):
                    if project_key(existing, position) == key:
                        merged[position] = replacement
                        break
            else:
                merged.append(replacement)
                seen_ids.add(key)

        self.model.set_projects(merged)
        self.dirty = True
        self.statusBar().showMessage("Merged external file changes with local edits", 6000)

    def new_project(self) -> None:
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            project = dialog.project()
            if self.project_id_exists(project["id"]):
                self.warn_duplicate_project_id(project["id"])
                return
            self.undo_stack.push(AddProjectCommand(self, project))
            self.mark_dirty("Project added")
            self.autosave_projects("Project added and saved")

    def selected_source_row(self) -> int | None:
        rows = self.selected_source_rows()
        if len(rows) != 1:
            return None
        return rows[0]

    def selected_source_rows(self) -> list[int]:
        indexes = self.table.selectionModel().selectedRows()
        rows = sorted({self.proxy.mapToSource(index).row() for index in indexes})
        return [row for row in rows if 0 <= row < len(self.model.projects)]

    def edit_selected_project(self) -> None:
        row = self.selected_source_row()
        if row is None:
            self.statusBar().showMessage("Select a project to edit", 4000)
            return
        dialog = ProjectDialog(self, self.model.projects[row])
        if dialog.exec() == QDialog.Accepted:
            project = dialog.project()
            if self.project_id_exists(project["id"], ignore_row=row):
                self.warn_duplicate_project_id(project["id"])
                return
            before = dict(self.model.projects[row])
            self.undo_stack.push(EditProjectCommand(self, row, before, project))
            self.mark_dirty("Project updated")
            self.autosave_projects("Project updated and saved")

    def duplicate_selected_project(self) -> None:
        row = self.selected_source_row()
        if row is None:
            return
        project = dict(self.model.projects[row])
        base_id = str(project.get("id", "project")).strip() or "project"
        copy_id = f"{base_id}-copy"
        suffix = 2
        while self.project_id_exists(copy_id):
            copy_id = f"{base_id}-copy-{suffix}"
            suffix += 1
        project["name"] = f"{project.get('name', 'Project')} Copy"
        project["id"] = copy_id
        self.undo_stack.push(DuplicateProjectCommand(self, len(self.model.projects), project))
        self.mark_dirty("Project duplicated")
        self.autosave_projects("Project duplicated and saved")

    def apply_magic_to_selected_names(self) -> None:
        rows = self.selected_source_rows()
        if not rows:
            self.statusBar().showMessage("Select one or more projects to apply magic names", 4000)
            return
        self.undo_stack.push(MagicNamesCommand(self, rows))
        self.mark_dirty("Magic names applied")
        self.autosave_projects("Magic names applied and saved")

    def project_page_url(self, project: dict[str, Any]) -> str:
        github_owner = str(self.settings.values.get("github_owner", "RiffPointer")).strip() or "RiffPointer"
        project_id = str(project.get("id", "")).strip()
        repo_url = str(project.get("repo_url") or project.get("github_url") or "").strip()
        if repo_url:
            return repo_url
        if project_id:
            return f"https://github.com/{github_owner}/{project_id}"
        return f"https://github.com/{github_owner}"

    def delete_selected_project(self) -> None:
        rows = self.selected_source_rows()
        if not rows:
            return
        confirm_delete = bool(self.settings.values.get("confirm_delete", True))
        should_delete = True
        if confirm_delete:
            if len(rows) == 1:
                project = self.model.projects[rows[0]]
                message = f"Delete '{project.get('name', 'this project')}'?"
            else:
                message = f"Delete {len(rows)} selected projects?"
            answer = QMessageBox.question(self, "Delete Project", message)
            should_delete = answer == QMessageBox.Yes
        if should_delete:
            if len(rows) == 1:
                project = self.model.projects[rows[0]]
                self.undo_stack.push(DeleteProjectCommand(self, rows[0], dict(project)))
            else:
                self.undo_stack.push(DeleteProjectsCommand(self, rows))
            self.mark_dirty("Projects deleted" if len(rows) > 1 else "Project deleted")
            self.autosave_projects("Projects deleted and saved" if len(rows) > 1 else "Project deleted and saved")

    def show_context_menu(self, position) -> None:
        clicked_index = self.table.indexAt(position)
        if clicked_index.isValid() and not self.table.selectionModel().isRowSelected(clicked_index.row(), QModelIndex()):
            self.table.selectRow(clicked_index.row())
        row = self.selected_source_row()
        selected_count = len(self.selected_source_rows())
        menu = QMenu(self)
        menu.addAction(self.edit_action)
        menu.addAction(self.duplicate_action)
        menu.addAction(self.delete_action)
        menu.addSeparator()
        open_project_page = menu.addAction("Open Project Page")
        open_demo = menu.addAction("Open Demo")
        copy_id = menu.addAction("Copy ID")
        self.edit_action.setEnabled(selected_count == 1)
        self.duplicate_action.setEnabled(selected_count == 1)
        self.delete_action.setEnabled(selected_count > 0)
        for action_item in (open_project_page, open_demo, copy_id):
            action_item.setEnabled(selected_count == 1)
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        if row is None or action is None:
            self._sync_selection_actions()
            return
        project = self.model.projects[row]
        project_id = str(project.get("id", ""))
        github_owner = str(self.settings.values.get("github_owner", "RiffPointer")).strip() or "RiffPointer"
        if action == open_project_page:
            webbrowser.open(self.project_page_url(project))
        elif action == open_demo:
            webbrowser.open(f"https://{github_owner.lower()}.github.io/{project_id}")
        elif action == copy_id:
            QApplication.clipboard().setText(project_id)
            self.statusBar().showMessage("Project ID copied", 3000)
        self._sync_selection_actions()

    def show_header_context_menu(self, position) -> None:
        header = self.table.horizontalHeader()
        column = header.logicalIndexAt(position)
        menu = QMenu(self)
        if column >= 0:
            visible = not self.table.isColumnHidden(column)
            toggle_action = menu.addAction(
                f"Hide {PROJECT_COLUMNS[column]}" if visible else f"Show {PROJECT_COLUMNS[column]}"
            )
            toggle_action.triggered.connect(
                lambda _checked=False, col=column: self.set_column_visible(col, not self.table.isColumnHidden(col))
            )
            menu.addSeparator()
        for action in getattr(self, "column_visibility_actions", []):
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction("Show All Columns", self.show_all_columns)
        menu.addAction("Hide All Columns", self.hide_all_columns)
        menu.exec(header.mapToGlobal(position))

    def open_preferences(self) -> None:
        dialog = PreferencesDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            new_path = Path(self.settings.values["project_data_path"]).expanduser()
            if new_path != self.data_path:
                if self.confirm_discard_changes():
                    self.data_path = new_path
                    self.load_projects()
            app = QApplication.instance()
            if app is not None:
                apply_theme(app, str(self.settings.values.get("theme", "auto")))
            self.apply_compact_mode(bool(self.settings.values.get("compact_mode", False)))
            self.statusBar().showMessage(f"Preferences saved to {self.settings.settings_path}", 6000)

    def check_links(self) -> None:
        progress = QProgressDialog("Checking project links...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Broken Link Detection")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.show()

        def report(value: int, message: str) -> None:
            progress.setValue(value)
            progress.setLabelText(message)
            QApplication.processEvents()

        try:
            result = check_project_links(
                self.model.projects,
                str(self.settings.values.get("github_owner", "RiffPointer")).strip() or "RiffPointer",
                lambda value, message: report(value, message),
            )
        finally:
            progress.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("Broken Link Detection")
        dialog.setMinimumWidth(780)
        layout = QVBoxLayout(dialog)
        summary = QLabel(f"Checked {result.checked} links. Issues found: {len(result.issues)}")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        issue_list = QListWidget()
        if result.issues:
            for issue in result.issues:
                issue_list.addItem(
                    QListWidgetItem(f"[{issue.issue_type}] {issue.label}: {issue.url} - {issue.detail}")
                )
        else:
            issue_list.addItem(QListWidgetItem("No broken links detected."))
        layout.addWidget(issue_list)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            "<b>{name}</b><br>"
            "Version: {version}<br><br>"
            "Repository: <a href=\"{repo}\">{repo}</a><br><br>"
            "Copyright 2026 RiffPointer<br>"
            "License: MIT<br><br>"
            "A native Windows-style PySide6 editor for the portfolio project data."
            .format(name=APP_NAME, version=APP_VERSION, repo=REPOSITORY_URL),
        )

    def mark_dirty(self, message: str) -> None:
        self.dirty = not self.undo_stack.isClean()
        self.statusBar().showMessage(f"{message}. Unsaved changes.", 5000)

    def _sync_dirty_state(self) -> None:
        self.dirty = not self.undo_stack.isClean()

    def confirm_discard_changes(self) -> bool:
        if not self.dirty:
            return True
        answer = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Discard unsaved changes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return answer == QMessageBox.Yes

    def closeEvent(self, event) -> None:
        if self.dirty:
            answer = QMessageBox.question(
                self,
                "Save Changes",
                "Save changes before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if answer == QMessageBox.Save:
                if not self.save_projects():
                    event.ignore()
                    return
            elif answer == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.adjust_column_widths()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.adjust_column_widths()

    def adjust_column_widths(self) -> None:
        table_width = self.table.width()
        if table_width > 100:
            target_width = int(table_width * 0.33)
            if self.table.columnWidth(0) < target_width:
                self.table.setColumnWidth(0, target_width)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    settings = SettingsManager()
    apply_theme(app, str(settings.values.get("theme", "auto")))

    # Gracefully exit on KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
    timer = QTimer()
    timer.start(200)
    timer.timeout.connect(lambda: None)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
